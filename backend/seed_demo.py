"""幂等初始化演示账号、实验室和设备。

在 backend 目录执行：python seed_demo.py
"""

from app.database import Base, SessionLocal, engine
from app.models.equipment import Equipment
from app.models.lab import Lab
from app.models.reservation import Reservation  # noqa: F401
from app.models.user import User
from app.utils.password import hash_password


def get_or_create_user(db, username: str, password: str, name: str, role: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(
        username=username,
        password=hash_password(password),
        name=name,
        role=role,
        status=1,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_lab(db, **values) -> Lab:
    lab = db.query(Lab).filter(Lab.name == values["name"]).first()
    if lab:
        return lab
    lab = Lab(**values)
    db.add(lab)
    db.flush()
    return lab


def get_or_create_equipment(db, lab: Lab, name: str, **values) -> Equipment:
    equipment = (
        db.query(Equipment)
        .filter(Equipment.lab_id == lab.id, Equipment.name == name)
        .first()
    )
    if equipment:
        return equipment
    equipment = Equipment(lab_id=lab.id, name=name, **values)
    db.add(equipment)
    db.flush()
    return equipment


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        get_or_create_user(db, "admin", "admin123", "系统管理员", "admin")
        get_or_create_user(db, "student", "student123", "演示学生", "student")

        ai_lab = get_or_create_lab(
            db,
            name="人工智能实验室",
            description="用于机器学习、深度学习与智能应用实验。",
            location="科技楼 A301",
            capacity=40,
            open_time="08:00",
            close_time="22:00",
            status=1,
        )
        chemistry_lab = get_or_create_lab(
            db,
            name="分析化学实验室",
            description="提供基础分析与精密仪器实验环境。",
            location="实验楼 B204",
            capacity=24,
            open_time="09:00",
            close_time="18:00",
            status=1,
        )

        get_or_create_equipment(
            db,
            ai_lab,
            "GPU 工作站",
            description="深度学习训练工作站",
            spec="RTX 5090 / 128GB RAM",
            quantity=8,
            status=1,
        )
        get_or_create_equipment(
            db,
            ai_lab,
            "智能机器人平台",
            description="移动机器人教学与算法验证平台",
            spec="ROS 2",
            quantity=4,
            status=1,
        )
        get_or_create_equipment(
            db,
            chemistry_lab,
            "高效液相色谱仪",
            description="样品成分分离与定量分析",
            spec="HPLC-2026",
            quantity=2,
            status=1,
        )
        db.commit()

    print("演示数据初始化完成")
    print("管理员：admin / admin123")
    print("学生：student / student123")


if __name__ == "__main__":
    main()
