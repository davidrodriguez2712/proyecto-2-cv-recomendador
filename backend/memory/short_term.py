from infra.cache.redis import get_redis
import json
from langchain_core.messages import BaseMessage

class ShortTermMemory:
    def __init__(self, max_messages = 20):
        self.max_messages = max_messages

    async def save_message(self, user: str, rol: str, content: str):
        """Guarda los mensajes de interacción del usuario y el agente"""
        redis = await get_redis()
        key = f"user:{user}:messages"

        await redis.rpush(
            key,
            json.dumps({"type": rol, "content": content})
        )
        await redis.ltrim(
            key,
            -self.max_messages,
            -1
        )
    
    # aca se requiere serializar el dict en save_message
    # Serializar significa convertir un objeto (estructura en memoria) en un formato
    # plano (texto o bytes) para poder guardarlo o enviarlo

    async def load_messages(self, user: str):
        """Carga los mensajes del usuario guardados en la memoria de corto plazo"""
        redis = await get_redis()
        key = f"user:{user}:messages"

        messages = await redis.lrange(
            key,
            0,
            -1
        )
        return messages[::-1]

    async def load_messages_lanchain(self, user: str):
        """Carga los mensajes pero enfocado a darle el formato para BaseMessage"""
        redis = await get_redis()
        key_user = f"user:{user}:messages"
        history_messages = await redis.lrange(
            key_user,
            -self.max_messages,
            -1
        )
        history_messages_json = [json.loads(conversation) for conversation in history_messages]
        history_messages_base_msg = [BaseMessage(**message) for message in history_messages_json]
        return history_messages_base_msg

















