from dataclasses import dataclass

@dataclass(frozen=True)
class ScaleConfig:
    customers: int
    products: int
    channels: int
    surveys: int
    survey_responses: int
    reviews: int
    support_messages: int

SCALES = {
    "starter": ScaleConfig(250, 12, 5, 8, 1000, 1000, 400),
    "full": ScaleConfig(10000, 40, 8, 20, 50000, 50000, 20000),
}
DEFAULT_SEED = 20261022
