from abc import ABCMeta
import os

from producer import KafkaProducerConfiguration

_PRODUCTION_ENVIRONMENT = "production"
_STAGING_ENVIRONMENT = "staging"
_LOCAL_ENVIRONMENT = "local"
_TESTING_ENVIRONMENT = "testing"


def get_config(environment):
    if environment == _PRODUCTION_ENVIRONMENT:
        return _ProductionAlertConfiguration()
    if environment == _LOCAL_ENVIRONMENT:
        return _LocalAlertConfiguration()
    if environment == _TESTING_ENVIRONMENT:
        return _TestingAlertConfiguration()
    if environment == _STAGING_ENVIRONMENT:
        pass


class AlertConfiguration(metaclass=ABCMeta):
    def __init__(self, environment):
        self._environment = environment

    def get_kafka_producer_configuration(self):
        return _KafkaProducerConfiguration(self._environment)


class _ProductionAlertConfiguration(AlertConfiguration):
    def __init__(self):
        super(self.__class__, self).__init__(_PRODUCTION_ENVIRONMENT)

    def get_kafka_ir_sensor_topic(self):
        return "irsensor-alerts-production"


class _LocalAlertConfiguration(AlertConfiguration):
    def __init__(self):
        super(self.__class__, self).__init__(_LOCAL_ENVIRONMENT)

    def get_kafka_ir_sensor_topic(self):
        return "irsensor-alerts-local"

    def get_kafka_ipc_topic(self):
        return "ipc-alerts-local"


class _TestingAlertConfiguration(AlertConfiguration):
    def __init__(self):
        super(self.__class__, self).__init__(_TESTING_ENVIRONMENT)

    def get_kafka_ir_sensor_topic(self):
        return "irsensor-alerts-local"

    def get_kafka_ipc_topic(self):
        return "ipc-alerts-local"


def _validated_get_from_env(environment_variable):
    value = os.getenv(environment_variable)
    if not value:
        raise ValueError(f"Environment variable `{environment_variable}` is not defined.")
    return value


def _get_kafka_bootstrap_servers(environment):
    if environment == _LOCAL_ENVIRONMENT:
        return os.getenv("KAFKA_HOST", "kafka:29092")
    try:
        return _validated_get_from_env(f"KAFKA_BOOTSTRAP_SERVERS")
    except ValueError:
        return None


class _KafkaProducerConfiguration(KafkaProducerConfiguration):
    def __init__(self, environment):
        self._environment = environment

    def get_bootstrap_servers(self):
        return _get_kafka_bootstrap_servers(self._environment)

    def get_flush_timeout(self):
        return float(os.getenv("KAFKA_PRODUCER_FLUSH_TIMEOUT_MS", "10000"))
