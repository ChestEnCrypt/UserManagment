import asyncio
from db_core import DBWorker, DBProducer

async def main():
    # поднимаем воркера‑потребителя очереди
    asyncio.create_task(DBWorker().run())
    db = DBProducer()

    # проверяем, свободны ли логин и телефон
    busy = await db.check_free(login="alice@example.com",
                               phone="+77000000001")
    print("занятость:", busy)
    if any(busy.values()):
        print("данные заняты, выходим")
        return

    # создаём пользователя
    await db.add_user(
        login="alice@example.com",
        password="secret123",
        full_name="Alice Ivanova",
        phone="+77000000001",
        role="admin"
    )
    print("аккаунт создан")

    # успешный вход
    ok = await db.auth(login="alice@example.com", password="secret123")
    print("успешный вход:", ok)

    # пять неправильных попыток — аккаунт будет заблокирован
    for n in range(5):
        res = await db.auth(login="alice@example.com", password="wrong")
        print(f"попытка {n+1} неверный пароль ->", res)

    # теперь даже правильный пароль не пройдёт
    blocked = await db.auth(login="alice@example.com", password="secret123")
    print("после блокировки вход невозможен:", blocked)

    # запрашиваем токен для сброса пароля
    token = await db.request_pwd_reset("alice@example.com")
    print("токен сброса:", token)

    # применяем новый пароль
    success = await db.reset_password(token, "newpass456")
    print("сброс пароля выполнен:", success)

    # снимаем блокировку (хотя reset_password уже обнулил счётчик)
    await db.unblock("alice@example.com")

    # подтверждаем e‑mail и телефон
    await db.confirm_email("alice@example.com")
    await db.confirm_phone("alice@example.com")

    # проверяем вход с новым паролем
    ok2 = await db.auth(login="alice@example.com", password="newpass456")
    print("вход с новым паролем:", ok2)

    # делаем резервную копию базы
    backup_path = await db.backup("after_flow")
    print("бэкап сохранён в:", backup_path)

    # немного ждём, чтобы воркер успел завершить транзакции
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
