from bloom import events


class Allocate(events.Event[str]):
    event_type: str = "BATCH_ALLOCATED"
