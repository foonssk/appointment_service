#!/bin/bash

# Очистка старых данных
echo "🧹 Cleaning up old containers and data..."
docker-compose down -v

# Удаление старых миграций
if [ -d "alembic/versions" ]; then
  echo "🗑️ Removing old migration versions..."
  rm -rf alembic/versions
fi

# Создаем структуру папок
mkdir -p alembic/versions scripts

# Создаем шаблон миграции Alembic
cat > alembic/script.py.mako << 'EOL'
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
EOL

# Записываем seed.py (если ещё не записан)
# cat > scripts/seed.py << 'EOL'
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.models.hospital import Hospital
# from app.models.doctor import Doctor
# from app.models.appointment import Appointment
# from datetime import date, time, datetime

# engine = create_engine("postgresql://postgres:postgres@db:5432/appointmet_db")
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def seed_data():
#     db = SessionLocal()

#     # Добавляем больницу
#     if not db.query(Hospital).filter_by(name="Central Hospital").first():
#         hospital = Hospital(name="Central Hospital", address="Main St 1")
#         db.add(hospital)
#         db.commit()
#         db.refresh(hospital)

#     # Добавляем врача
#     if not db.query(Doctor).filter_by(name="Dr. John Smith").first():
#         doctor = Doctor(
#             name="Dr. John Smith",
#             hospital_id=1,
#             work_day=date(2025, 4, 5),
#             shift_start=time(9, 0),
#             shift_end=time(17, 0)
#         )
#         db.add(doctor)
#         db.commit()
#         db.refresh(doctor)

#     # Добавляем запись
#     if not db.query(Appointment).filter_by(patient_id=1001).first():
#         appointment = Appointment(
#             doctor_id=1,
#             patient_id=1001,
#             appointment_date=datetime(2025, 4, 5, 10, 0)
#         )
#         db.add(appointment)
#         db.commit()

#     print("✅ Seed data added successfully.")
#     db.close()


# if __name__ == "__main__":
#     seed_data()
# EOL

# Запуск базы данных
echo "🔄 Starting database and Redis..."
docker-compose up -d db redis

# Ждём готовности
echo "⏳ Waiting for database to be ready..."
sleep 5

# Генерируем миграцию
echo "🔄 Generating new migration..."
docker-compose run --rm app alembic revision --autogenerate -m "Initial tables"

# Сбрасываем миграции и применяем заново
echo "🔁 Downgrading to base..."
docker-compose run --rm app alembic downgrade base || true

echo "🆙 Upgrading to head..."
docker-compose run --rm app alembic upgrade head

# Заполняем данными
echo "🌱 Running seed script..."
docker-compose run --rm app python /app/scripts/seed.py

# Запускаем приложение
echo "🚀 Starting the application..."
docker-compose up -d app