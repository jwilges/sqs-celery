broker_url = 'redis://redis:6379/0'
broker_transport_options = {
    'visibility_timeout': 3600, # set to longest ETA
}
result_backend = 'redis://redis:6379/0'