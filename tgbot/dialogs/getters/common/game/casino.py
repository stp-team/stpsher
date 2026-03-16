"""Геттеры для казино."""

from typing import Dict

from aiogram_dialog import DialogManager
from stp_database.models.STP import Employee
from stp_database.repo.STP import MainRequestsRepo

# Иконки для разных игр
GAME_ICONS = {
    "slots": "🎰",
    "dice": "🎲",
    "darts": "🎯",
    "bowling": "🎳",
}


async def balance_getter(stp_repo: MainRequestsRepo, user: Employee, **_kwargs) -> Dict:
    """Геттер для получения баланса пользователя.

    Args:
        user: Экземпляр пользователя с моделью Employee
        stp_repo: Репозиторий операций с базой STP

    Returns:
        Словарь с балансом пользователя
    """
    #user_balance = await stp_repo.transaction.get_user_balance(user.user_id)
    transaction_user_id = user.employee_id
    user_balance = await stp_repo.transaction.get_user_balance(transaction_user_id)

    return {
        "balance": user_balance,
        "is_casino_allowed": user.is_casino_allowed,
    }


async def casino_game_getter(
    stp_repo: MainRequestsRepo,
    user: Employee,
    dialog_manager: DialogManager,
    **_kwargs,
) -> Dict:
    """Геттер для игрового окна казино.

    Args:
        stp_repo: Репозиторий операций с базой STP
        user: Экземпляр пользователя с моделью Employee
        dialog_manager: Менеджер диалога

    Returns:
        Словарь с балансом и текущей ставкой
    """
    #user_balance = await stp_repo.transaction.get_user_balance(user.user_id)
    transaction_user_id = user.employee_id
    user_balance = await stp_repo.transaction.get_user_balance(transaction_user_id)

    # Если ставка не установлена, устанавливаем 10% от баланса (минимум 10)
    if "casino_rate" not in dialog_manager.dialog_data:
        default_rate = max(10, int(user_balance * 0.1))
        dialog_manager.dialog_data["casino_rate"] = default_rate

    # Получаем текущую ставку из контекста диалога
    current_rate = dialog_manager.dialog_data.get("casino_rate", 10)

    # Рассчитываем доступные изменения ставки
    show_minus_500 = current_rate >= 510
    show_minus_100 = current_rate >= 110
    show_minus_50 = current_rate >= 60
    show_minus_10 = current_rate >= 20

    show_plus_10 = user_balance >= current_rate + 10
    show_plus_50 = user_balance >= current_rate + 50
    show_plus_100 = user_balance >= current_rate + 100
    show_plus_500 = user_balance >= current_rate + 500

    return {
        "balance": user_balance,
        "current_rate": current_rate,
        "show_minus_500": show_minus_500,
        "show_minus_100": show_minus_100,
        "show_minus_50": show_minus_50,
        "show_minus_10": show_minus_10,
        "show_plus_10": show_plus_10,
        "show_plus_50": show_plus_50,
        "show_plus_100": show_plus_100,
        "show_plus_500": show_plus_500,
        "is_casino_allowed": user.is_casino_allowed,
    }


async def casino_waiting_getter(
    dialog_manager: DialogManager,
    user: Employee,
    **_kwargs,
) -> Dict:
    """Геттер для окна ожидания результата игры.

    Args:
        dialog_manager: Менеджер диалога
        user: Экземпляр пользователя с моделью Employee

    Returns:
        Словарь с иконкой игры и ставкой
    """
    game_type = dialog_manager.dialog_data.get("casino_game_type", "slots")
    current_rate = dialog_manager.dialog_data.get("casino_rate", 10)

    return {
        "game_icon": GAME_ICONS.get(game_type, "🎰"),
        "current_rate": current_rate,
        "is_casino_allowed": user.is_casino_allowed,
    }


async def casino_result_getter(
    stp_repo: MainRequestsRepo,
    user: Employee,
    dialog_manager: DialogManager,
    **_kwargs,
) -> Dict:
    """Геттер для окна результата игры.

    Args:
        stp_repo: Репозиторий операций с базой STP
        user: Текущий пользователь
        dialog_manager: Менеджер диалога

    Returns:
        Словарь с результатами игры
    """
    #user_balance = await stp_repo.transaction.get_user_balance(user.user_id)
    transaction_user_id = user.employee_id
    user_balance = await stp_repo.transaction.get_user_balance(transaction_user_id)

    # Получаем результаты из dialog_data
    result_icon = dialog_manager.dialog_data.get("result_icon", "❌")
    result_title = dialog_manager.dialog_data.get("result_title", "Результат")
    result_message = dialog_manager.dialog_data.get("result_message", "")
    bet_amount = dialog_manager.dialog_data.get("casino_rate", 10)
    win_amount = dialog_manager.dialog_data.get("win_amount", 0)
    old_balance = dialog_manager.dialog_data.get("old_balance", user_balance)

    # Формируем сообщение о выигрыше/проигрыше
    if win_amount > 0:
        # Получаем множитель из dialog_data
        multiplier = dialog_manager.dialog_data.get("multiplier", 0)

        if multiplier > 0:
            gross_win = int(bet_amount * multiplier)
            win_message = (
                f"💰 <b>Выигрыш:</b> {gross_win} баллов → прибыль +{win_amount}"
            )
        else:
            win_message = f"🎉 <b>Выигрыш:</b> +{win_amount} баллов"
    elif win_amount < 0:
        win_message = f"💸 <b>Проигрыш:</b> {abs(win_amount)} баллов"
    else:
        win_message = "➖ <b>Без изменений</b>"

    # Формируем строку баланса
    balance_display = f"{old_balance} → {user_balance} баллов"

    return {
        "result_icon": result_icon,
        "result_title": result_title,
        "result_message": result_message,
        "bet_amount": bet_amount,
        "win_amount": win_amount,
        "win_message": win_message,
        "balance": balance_display,
        "is_casino_allowed": user.is_casino_allowed,
    }
