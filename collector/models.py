# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from database import Base

class LoginEvent(Base):
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # original event timestamp from agent (string or ISO8601)
    event_timestamp = Column(String, index=True)

    hostname = Column(String, index=True)
    user = Column(String, index=True)
    method = Column(String, index=True)
    source_ip = Column(String, index=True)
    source_port = Column(String)

    raw_message = Column(String)

    # extra metadata
    region = Column(String, index=True, nullable=True)
    host_group = Column(String, index=True, nullable=True)
    severity = Column(String, index=True, nullable=True)  # e.g. low/medium/high
    flagged = Column(Boolean, default=False, index=True)  # was this “interesting”?


class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)