import sentry_sdk, os
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry_sdk():
    sentry_result = sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        send_default_pii=True,
        enable_logs=True,
        traces_sample_rate=1.0
    )
    return sentry_result
