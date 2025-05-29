

тут дизинфа.


# Helm Chart для Transcriber

## Структура чарта

```
helm/
├── Chart.yaml              # Метаданные чарта
├── values.yaml            # Базовые значения по умолчанию
├── values-dev.yaml        # Конфигурация для development
├── values-prod.yaml       # Конфигурация для production
├── templates/             # Шаблоны манифестов
│   ├── namespace.yaml
│   ├── postgres-secret.yaml
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   ├── app-ingress.yaml
│   ├── _helpers.tpl      # Вспомогательные шаблоны
│   └── NOTES.txt         # Информация после установки
└── .helmignore           # Игнорируемые файлы
```

## Установка

1. Установите Helm (если еще не установлен):
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

2. Подготовьте секреты для PostgreSQL:
```bash
# Закодируйте значения в base64
echo -n "your_username" | base64
echo -n "your_password" | base64
echo -n "your_database" | base64
```

3. Установите чарт:

### Development окружение
```bash
helm install transcriber ./helm \
  --namespace transcriber \
  --create-namespace \
  -f helm/values-dev.yaml \
  --set postgresql.secret.username=your_username \
  --set postgresql.secret.password=your_password \
  --set postgresql.secret.database=your_database
```

### Production окружение
```bash
helm install transcriber ./helm \
  --namespace transcriber \
  --create-namespace \
  -f helm/values-prod.yaml \
  --set postgresql.secret.username=your_username \
  --set postgresql.secret.password=your_password \
  --set postgresql.secret.database=your_database
```

## Обновление

```bash
# Для development
helm upgrade transcriber ./helm \
  --namespace transcriber \
  -f helm/values-dev.yaml

# Для production
helm upgrade transcriber ./helm \
  --namespace transcriber \
  -f helm/values-prod.yaml
```

## Удаление

```bash
helm uninstall transcriber --namespace transcriber
```

## Конфигурация

### Файлы конфигурации

- `values.yaml` - базовые значения по умолчанию
- `values-dev.yaml` - переопределения для development
- `values-prod.yaml` - переопределения для production

### Основные параметры

#### Глобальные настройки
- `global.namespace` - namespace для всех ресурсов
- `global.environment` - тип окружения (development/production)

#### Приложение
- `app.replicaCount` - количество реплик
- `app.resources` - ресурсы для контейнера
- `app.ingress.host` - хост для Ingress
- `app.image.tag` - тег образа
- `app.service.type` - тип сервиса (LoadBalancer/ClusterIP)

#### PostgreSQL
- `postgresql.enabled` - включить/выключить PostgreSQL
- `postgresql.persistence.size` - размер PVC
- `postgresql.resources` - ресурсы для PostgreSQL
- `postgresql.secret.*` - секреты для подключения

### Различия между окружениями

#### Development
- Меньше реплик (1)
- Меньше ресурсов
- Локальный хост (transcriber-dev.local)
- Базовые настройки Ingress

#### Production
- Больше реплик (2)
- Больше ресурсов
- Продакшн домен
- SSL/TLS настройки
- Увеличенный размер PVC

## Проверка статуса

```bash
# Проверка релиза
helm status transcriber -n transcriber

# Проверка всех ресурсов
kubectl get all -n transcriber

# Проверка логов
kubectl logs -f deployment/transcriber-app -n transcriber

# Проверка Ingress
kubectl get ingress -n transcriber
```

## Доступ к приложению

### Development
- http://transcriber-dev.local

### Production
- https://transcriber.example.com

## Устранение неполадок

1. Проверьте статус подов:
```bash
kubectl get pods -n transcriber
```

2. Проверьте логи:
```bash
kubectl logs -f deployment/transcriber-app -n transcriber
```

3. Проверьте конфигурацию:
```bash
helm get values transcriber -n transcriber
```

4. Проверьте события:
```bash
kubectl get events -n transcriber
``` 