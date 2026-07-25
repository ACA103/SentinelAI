"""
Implements: 02_Data/06_SYNTHETIC_DATA_GENERATION.md
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from pathlib import Path
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DepartmentGenerator:
    def __init__(self, fake: Faker):
        self.fake = fake

    def generate(self, config: dict) -> pd.DataFrame:
        num_departments = config.get("num_departments", 8)
        data = []
        departments = [
            "HR", "Finance", "Engineering", "Sales", "IT Support",
            "Marketing", "Legal", "Operations", "Contractors", "Service Accounts"
        ]
        for i in range(1, num_departments + 1):
            data.append({
                "department_id": i,
                "department_name": departments[i % len(departments)],
                "work_start_hour": random.choice([7, 8, 9, 20]), # Including shift workers
                "work_end_hour": random.choice([16, 17, 18, 6])
            })
        return pd.DataFrame(data)

class UserGenerator:
    def __init__(self, fake: Faker):
        self.fake = fake

    def generate(self, config: dict, departments: pd.DataFrame) -> pd.DataFrame:
        num_users = config.get("num_users", 1000)
        data = []
        dept_ids = departments["department_id"].tolist()
        
        for i in range(1, num_users + 1):
            role_type = random.choice(["Office Worker", "Remote Employee", "Hybrid Worker", "Contractor", "Service Account"])
            data.append({
                "user_id": i,
                "employee_id": f"EMP{i:05d}" if role_type != "Service Account" else f"SVC{i:05d}",
                "name": self.fake.name(),
                "email": self.fake.email(),
                "department_id": random.choice(dept_ids),
                "role": role_type,
                "privilege_level": random.randint(1, 5) if role_type != "Service Account" else 5,
                "office_location": self.fake.city() if "Remote" not in role_type else "Remote",
                "employment_status": "Active",
                "created_at": datetime.now() - timedelta(days=random.randint(30, 365))
            })
        return pd.DataFrame(data)

class DeviceGenerator:
    def __init__(self, fake: Faker):
        self.fake = fake

    def generate(self, config: dict, users: pd.DataFrame) -> pd.DataFrame:
        num_devices = config.get("num_devices", 1800)
        data = []
        user_ids = users["user_id"].tolist()
        
        for i in range(1, num_devices + 1):
            data.append({
                "device_id": i,
                "user_id": random.choice(user_ids),
                "device_type": random.choice(["Laptop", "Mobile", "Desktop"]),
                "operating_system": random.choice(["Windows", "macOS", "Linux"]),
                "browser": random.choice(["Chrome", "Firefox", "Edge"]),
                "trust_status": random.choice([True, False]),
                "fingerprint": self.fake.sha256(),
                "registration_date": datetime.now() - timedelta(days=180)
            })
        return pd.DataFrame(data)

class ResourceGenerator:
    def __init__(self, fake: Faker):
        self.fake = fake

    def generate(self, config: dict, departments: pd.DataFrame) -> pd.DataFrame:
        num_resources = config.get("num_resources", 30)
        data = []
        dept_ids = departments["department_id"].tolist()
        
        for i in range(1, num_resources + 1):
            data.append({
                "resource_id": i,
                "resource_name": f"App_{self.fake.word()}",
                "department_id": random.choice(dept_ids),
                "sensitivity_level": random.randint(1, 5),
                "requires_mfa": random.choice([True, False])
            })
        return pd.DataFrame(data)

class AuthenticationGenerator:
    def __init__(self, fake: Faker):
        self.fake = fake

    def generate(self, config: dict, users: pd.DataFrame, devices: pd.DataFrame, resources: pd.DataFrame) -> pd.DataFrame:
        num_events = config.get("num_events", 10000)
        user_ids = users["user_id"].tolist()
        device_ids = devices["device_id"].tolist()
        resource_ids = resources["resource_id"].tolist()
        
        data = []
        base_time = datetime.now() - timedelta(days=config.get("simulation_days", 90))
        
        for i in range(1, num_events + 1):
            data.append({
                "event_id": i,
                "timestamp": base_time + timedelta(minutes=random.randint(1, 120000)),
                "user_id": random.choice(user_ids),
                "device_id": random.choice(device_ids),
                "session_id": random.randint(1, max(1, num_events // 5)),
                "resource_id": random.choice(resource_ids),
                "ip_address": self.fake.ipv4_private(),
                "country": "USA",
                "city": self.fake.city(),
                "latitude": float(self.fake.latitude()),
                "longitude": float(self.fake.longitude()),
                "authentication_method": random.choice(["Password", "MFA", "SSO"]),
                "authentication_result": "Success" if random.random() > 0.05 else "Failure",
                "failure_reason": None,
                "attack_label": 0,
                "is_attack": False
            })
            
        df = pd.DataFrame(data)
        # Ensure chronological order
        df = df.sort_values("timestamp").reset_index(drop=True)
        df["event_id"] = df.index + 1
        return df

class SessionGenerator:
    def generate(self, events: pd.DataFrame) -> pd.DataFrame:
        data = []
        for session_id, group in events.groupby("session_id"):
            login_time = group["timestamp"].min()
            logout_time = group["timestamp"].max() + timedelta(minutes=random.randint(5, 120))
            data.append({
                "session_id": session_id,
                "user_id": group["user_id"].iloc[0],
                "login_time": login_time,
                "logout_time": logout_time,
                "duration_minutes": (logout_time - login_time).total_seconds() / 60,
                "resource_count": group["resource_id"].nunique(),
                "total_events": len(group)
            })
        return pd.DataFrame(data)

class AttackInjector:
    def __init__(self, fake: Faker):
        self.fake = fake

    def inject(self, config: dict, events: pd.DataFrame) -> pd.DataFrame:
        scenario = config.get("scenario", "Mixed Enterprise Attack")
        attack_ratio = config.get("attack_percentage", 0.03)
        if scenario == "Normal Activity":
            attack_ratio = 0.001 # Keep a tiny bit of noise or 0
        
        num_attacks = int(len(events) * attack_ratio)
        
        attack_indices = random.sample(range(len(events)), num_attacks)
        
        label_map = {
            "Credential Stuffing": 1,
            "Password Spray": 2,
            "Brute Force": 3,
            "Impossible Travel": 4,
            "Insider Threat": 5,
            "Privilege Escalation": 6,
            "Lateral Movement": 7,
            "Low-and-Slow Exfiltration": 7
        }
        
        for idx in attack_indices:
            if scenario == "Mixed Enterprise Attack" or scenario == "Normal Activity":
                attack_type = random.choice([
                    "Brute Force", "Credential Stuffing", "Password Spray",
                    "Impossible Travel", "Insider Threat", "Lateral Movement",
                    "Privilege Escalation", "Low-and-Slow Exfiltration"
                ])
            else:
                # Map scenario name to label name
                scenario_map = {
                    "Brute Force Attack": "Brute Force",
                    "Credential Stuffing": "Credential Stuffing",
                    "Password Spray": "Password Spray",
                    "Impossible Travel": "Impossible Travel",
                    "Insider Threat": "Insider Threat",
                    "Suspicious Device": "Lateral Movement"
                }
                attack_type = scenario_map.get(scenario, "Brute Force")
            
            is_failure = attack_type in ["Brute Force", "Password Spray"]
            
            events.at[idx, "is_attack"] = True
            events.at[idx, "attack_label"] = label_map[attack_type]
            events.at[idx, "authentication_result"] = "Failure" if is_failure else "Success"
            events.at[idx, "failure_reason"] = "Invalid Password" if is_failure else None
            events.at[idx, "country"] = self.fake.country()
            events.at[idx, "ip_address"] = self.fake.ipv4_public()
            
        return events

class SyntheticDataGenerator:
    """
    Implements: 02_Data/06_SYNTHETIC_DATA_GENERATION.md
    Orchestrates the sequential generation pipeline.
    """
    def __init__(self, config_overrides=None):
        self.config = config_overrides or {}
        self.seed = self.config.get("seed", 42)
        
        self.fake = Faker()
        Faker.seed(self.seed)
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        self.dept_gen = DepartmentGenerator(self.fake)
        self.user_gen = UserGenerator(self.fake)
        self.device_gen = DeviceGenerator(self.fake)
        self.res_gen = ResourceGenerator(self.fake)
        self.auth_gen = AuthenticationGenerator(self.fake)
        self.session_gen = SessionGenerator()
        self.injector = AttackInjector(self.fake)

    def generate(self) -> Dict[str, pd.DataFrame]:
        logger.info("Stage 2: Generate organization")
        departments = self.dept_gen.generate(self.config)
        
        logger.info("Stage 3: Generate users")
        users = self.user_gen.generate(self.config, departments)
        
        logger.info("Stage 4: Assign devices")
        devices = self.device_gen.generate(self.config, users)
        
        logger.info("Stage 5: Generate resources")
        resources = self.res_gen.generate(self.config, departments)
        
        logger.info("Stage 6: Generate authentication events")
        events = self.auth_gen.generate(self.config, users, devices, resources)
        
        logger.info("Stage 7: Generate sessions")
        sessions = self.session_gen.generate(events)
        
        logger.info("Stage 8: Inject attacks")
        events = self.injector.inject(self.config, events)
        
        return {
            "departments": departments,
            "users": users,
            "devices": devices,
            "resources": resources,
            "authentication_events": events,
            "sessions": sessions
        }
