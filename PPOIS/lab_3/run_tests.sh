#!/bin/bash

echo "Запуск тестов с покрытием кода..."
echo ""

python -m pytest --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "✓ HTML отчет создан в htmlcov/index.html"
