# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, String, TIMESTAMP, Table, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Dormitory(Base):
    __tablename__ = 'dormitories'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    code = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class Migration(Base):
    __tablename__ = 'migrations'

    id = Column(INTEGER(10), primary_key=True)
    migration = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    batch = Column(INTEGER(11), nullable=False)


t_password_resets = Table(
    'password_resets', metadata,
    Column('email', String(255, 'utf8mb4_unicode_ci'), nullable=False, index=True),
    Column('token', String(255, 'utf8mb4_unicode_ci'), nullable=False),
    Column('created_at', TIMESTAMP)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    email = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True)
    email_verified_at = Column(TIMESTAMP)
    password = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    api_token = Column(String(80, 'utf8mb4_unicode_ci'), unique=True)
    role = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    wechat_qrcode = Column(String(255, 'utf8mb4_unicode_ci'))
    wechat_id = Column(String(255, 'utf8mb4_unicode_ci'))
    remember_token = Column(String(100, 'utf8mb4_unicode_ci'))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class Jaccount(Base):
    __tablename__ = 'jaccounts'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    jaccount = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    code = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship('User')


class Lock(Base):
    __tablename__ = 'locks'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    dormitory_id = Column(ForeignKey('dormitories.id'), nullable=False, index=True)
    hid = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    dormitory = relationship('Dormitory')


class RoomRecord(Base):
    __tablename__ = 'room_records'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    code = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    dormitory_id = Column(ForeignKey('dormitories.id'), nullable=False, index=True)
    room = Column(INTEGER(11), nullable=False)
    verified = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    dormitory = relationship('Dormitory')


class UnlockRecord(Base):
    __tablename__ = 'unlock_records'

    id = Column(String(255, 'utf8mb4_unicode_ci'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    lock_id = Column(ForeignKey('locks.id'), nullable=False, index=True)
    latitude = Column(Float(asdecimal=True))
    longitude = Column(Float(asdecimal=True))
    success = Column(TINYINT(1), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    lock = relationship('Lock')
    user = relationship('User')
