import logging

from stp_database.models.STP import Employee
from stp_database.repo.STP import MainRequestsRepo

logger = logging.getLogger(__name__)


async def normalize_transaction_user_id_for_employee(
    employee: Employee, stp_repo: MainRequestsRepo
) -> int:
    """Переносит транзакции сотрудника с Telegram ID на employee.employee_id.

    В legacy-данных ``transactions.user_id`` может хранить ``employee.user_id``.
    Для нового формата переносим такие записи на ``employee.employee_id``.

    Args:
        employee: Сотрудник, для которого выполняем нормализацию
        stp_repo: Репозиторий STP

    Returns:
        Количество обновлённых транзакций
    """
    if (
        not employee.user_id
        or not employee.employee_id
        or employee.user_id == employee.employee_id
    ):
        return 0

    legacy_transactions = await stp_repo.transaction.get_user_transactions(
        user_id=employee.user_id
    )

    updated_count = 0
    for transaction in legacy_transactions:
        if transaction.user_id != employee.user_id:
            continue

        updated_transaction = await stp_repo.transaction.update_transaction(
            transaction_id=transaction.id,
            user_id=employee.employee_id,
        )
        if updated_transaction:
            updated_count += 1

    if updated_count:
        logger.info(
            "Нормализованы транзакции сотрудника %s: %s шт. (%s -> %s)",
            employee.fullname,
            updated_count,
            employee.user_id,
            employee.employee_id,
        )

    return updated_count