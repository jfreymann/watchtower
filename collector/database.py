# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:////var/lib/watchtower/watchtower.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
