"""Геттеры для меню магазина специалистов."""

from typing import Any, Dict

from aiogram_dialog import DialogManager
from stp_database.models.STP import Employee
from stp_database.repo.STP import MainRequestsRepo


async def products_getter(
    user: Employee, stp_repo: MainRequestsRepo, division: str | None = None, **_kwargs
) -> Dict[str, Any]:
    """Геттер для получения списка предметов магазина.

    Args:
        user: Экземпляр пользователя с моделью Employee
        stp_repo: Репозиторий операций с базой STP
        division: Фильтр по подразделению (опционально)

    Returns:
        Словарь из списка предметов и баланса сотрудника
    """
    user_balance: int = await stp_repo.transaction.get_user_balance(
        user_id=user.user_id
    )

    # Получаем все продукты для указанного подразделения
    if division == "all":
        all_products = await stp_repo.product.get_products(
            division=user.division, role=user.role
        )
    else:
        all_products = await stp_repo.product.get_available_products(
            user_balance, division=user.division, user_role=user.role
        )

    # Фильтруем продукты по buyer_roles пользователя:
    # В МАГАЗИНЕ показываем только те продукты, которые пользователь может КУПИТЬ
    # (роль пользователя в buyer_roles)
    # Продукты, где пользователь является менеджером (manager_role), в магазине НЕ показываем
    products = []
    for product in all_products:
        # Проверяем, может ли пользователь купить этот продукт
        can_buy = False

        # Проверка buyer_roles: продукт доступен для покупки, если buyer_roles пустой/None
        # ИЛИ содержит роль пользователя
        if product.buyer_roles is None or product.buyer_roles == []:
            can_buy = True
        elif user.role in product.buyer_roles:
            can_buy = True

        if can_buy:
            products.append(product)

    formatted_products = []
    for product in products:
        formatted_products.append((
            product.id,
            product.name,
            product.description,
            product.count,
            product.cost,
            product.division,
        ))

    return {
        "products": formatted_products,
        "user_balance": user_balance,
    }


async def confirmation_getter(
    dialog_manager: DialogManager, **_kwargs
) -> Dict[str, Any]:
    """Геттер для окна подтверждения покупки предмета.

    Args:
        dialog_manager: Менеджер диалога

    Returns:
        Словарь с информацией о выбранном предмете для покупки
    """
    product_info = dialog_manager.dialog_data.get("selected_product")
    user_balance = dialog_manager.dialog_data.get("user_balance", 0)

    if not product_info:
        return {}

    balance_after_purchase = user_balance - product_info["cost"]

    return {
        "product_name": product_info["name"],
        "product_description": product_info["description"],
        "product_count": product_info["count"],
        "product_cost": product_info["cost"],
        "user_balance": user_balance,
        "balance_after_purchase": balance_after_purchase,
    }


async def success_getter(dialog_manager: DialogManager, **_kwargs) -> Dict[str, Any]:
    """Геттер для окна успешной покупки предмета.

    Args:
        dialog_manager: Менеджер диалога

    Returns:
        Словарь с информацией о приобретенном предмете и изменении баланса
    """
    product_info = dialog_manager.dialog_data.get("selected_product")
    user_balance = dialog_manager.dialog_data.get("user_balance", 0)
    new_balance = dialog_manager.dialog_data.get("new_balance", 0)

    if not product_info:
        return {}

    return {
        "product_name": product_info["name"],
        "product_description": product_info["description"],
        "product_count": product_info["count"],
        "product_cost": product_info["cost"],
        "user_balance": user_balance,
        "new_balance": new_balance,
    }
