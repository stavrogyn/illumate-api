#!/usr/bin/env python3
"""
Integration test for real email sending via AWS SES
"""

import os
import sys
import pytest
from app.infrastructure.external.email_service import EmailService
from app.config import settings

def test_email_sending():
    """Тестирует отправку реальных писем"""
    
    print("=== Тестирование реальной отправки писем ===\n")
    
    # Проверяем переменные окружения через config
    required_vars = [
        ("AWS_REGION", settings.aws_region),
        ("AWS_ACCESS_KEY_ID", settings.aws_access_key_id), 
        ("AWS_SECRET_ACCESS_KEY", settings.aws_secret_access_key),
        ("SENDER_EMAIL", settings.sender_email)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nДля тестирования реальной отправки писем нужно:")
        print("1. Установить переменные окружения:")
        print("   export AWS_REGION=eu-north-1")
        print("   export AWS_ACCESS_KEY_ID=your-access-key-id")
        print("   export AWS_SECRET_ACCESS_KEY=your-secret-access-key")
        print("   export SENDER_EMAIL=your-verified-email@example.com")
        print("\n2. Верифицировать email-адреса в AWS SES:")
        print("   - Отправитель (SENDER_EMAIL) - обязательно")
        print("   - Получатели - если в sandbox режиме")
        pytest.skip("Missing AWS SES environment variables")
    
    print("✅ Все переменные окружения установлены")
    print(f"   AWS_REGION: {settings.aws_region}")
    print(f"   SENDER_EMAIL: {settings.sender_email}")
    print(f"   AWS_ACCESS_KEY_ID: {settings.aws_access_key_id[:10]}...")
    
    # Создаем email service
    email_service = EmailService()
    
    if not email_service.ses_client:
        print("❌ Не удалось инициализировать AWS SES клиент")
        pytest.skip("AWS SES client initialization failed")
    
    # Тестируем отправку простого письма
    print("\n📧 Тестирование отправки простого письма...")
    
    # Use a test email or skip if not provided
    test_email = os.getenv("TEST_EMAIL")
    if not test_email:
        print("⏭️ Пропускаем тест отправки (TEST_EMAIL не установлен)")
        print("Для тестирования установите: export TEST_EMAIL=your-test-email@example.com")
        pytest.skip("TEST_EMAIL environment variable not set")
    
    success = email_service.send_email(
        to_email=test_email,
        subject="Тестовое письмо от FastAPI Auth System",
        body_text="Это тестовое письмо для проверки работы AWS SES.",
        body_html="<h1>Тестовое письмо</h1><p>Это тестовое письмо для проверки работы AWS SES.</p>"
    )
    
    if success:
        print("✅ Письмо отправлено успешно!")
        assert True
    else:
        print("❌ Ошибка отправки письма")
        assert False

def show_aws_ses_setup_instructions():
    """Показывает инструкции по настройке AWS SES"""
    
    print("\n" + "="*60)
    print("ИНСТРУКЦИИ ПО НАСТРОЙКЕ AWS SES")
    print("="*60)
    
    print("\n1. Создайте аккаунт AWS и перейдите в SES")
    print("2. Выберите регион (например, eu-north-1)")
    print("3. Верифицируйте отправителя:")
    print("   - Перейдите в 'Verified identities'")
    print("   - Нажмите 'Create identity'")
    print("   - Выберите 'Email address'")
    print("   - Введите ваш email")
    print("   - Подтвердите email через письмо от AWS")
    
    print("\n4. Создайте IAM пользователя с правами SES:")
    print("   - Перейдите в IAM")
    print("   - Создайте пользователя")
    print("   - Прикрепите политику 'AmazonSESFullAccess'")
    print("   - Сохраните Access Key ID и Secret Access Key")
    
    print("\n5. Установите переменные окружения:")
    print("   export AWS_REGION=eu-north-1")
    print("   export AWS_ACCESS_KEY_ID=your-access-key-id")
    print("   export AWS_SECRET_ACCESS_KEY=your-secret-access-key")
    print("   export SENDER_EMAIL=your-verified-email@example.com")
    
    print("\n6. Если вы в sandbox режиме:")
    print("   - Верифицируйте все email-адреса получателей")
    print("   - Или запросите выход из sandbox режима")
    
    print("\n7. Для production:")
    print("   - Запросите увеличение лимитов")
    print("   - Настройте DKIM для домена")
    print("   - Настройте обратную связь (bounce/complaint handling)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_aws_ses_setup_instructions()
    else:
        # This allows running the file directly for manual testing
        test_email_sending()
        show_aws_ses_setup_instructions() 
