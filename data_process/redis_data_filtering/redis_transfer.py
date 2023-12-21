import os
# this file is used to tranfer data from one redis to another, we do not expect to use it more than once
os.environ[
    "REDIS_OM_URL"
] = "redis://:aclkasjf29qwrUOIO@tiger.lti.cs.cmu.edu:6388"
# path to migrant: "redis://:auess29aknfl2jro20W@tiger.lti.cs.cmu.edu:6377"

from redis_om import Migrator

from sotopia.database.logs import EpisodeLog
import json
from sotopia.database.persistent_profile import (
    AgentProfile,
    EnvironmentProfile,
    RelationshipProfile,
)
from sotopia.database.env_agent_combo_storage import EnvAgentComboStorage

# res_pks = list(RelationshipProfile.all_pks()) # 120
# env_agent_combos = list(EnvAgentComboStorage.all_pks()) # 550
# agent_pks = list(AgentProfile.all_pks()) # 40
# env_pks = list(EnvironmentProfile.all_pks()) # 62
# epi_pks = list(EpisodeLog.all_pks()) 
# all_combs = list(env_agent_combos)

def load_object_to_json(pks, objecttype, path):
    for pk in pks:
        objectp = objecttype.get(pk = pk)
        objectp_json = objectp.json()
        with open(os.path.join(path, f"{pk}.json"), 'w') as f:
            f.write(objectp_json)

# E.G load_object_to_json(res_pks, RelationshipProfile, "/DIR/redis_combo")

path = "/DIR/redis_combo"

def upload_json_to_db(filepath, objecttype):
    for filename in os.listdir(filepath):
        if filename == '.DS_Store':
            continue
        with open(os.path.join(filepath, filename), 'r') as f:
            jsonfile = json.load(f)
            newobject = objecttype(**jsonfile)
            newobject.save()

Migrator().run()
upload_json_to_db(path, EnvAgentComboStorage)