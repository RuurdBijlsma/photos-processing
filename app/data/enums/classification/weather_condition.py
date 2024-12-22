from enum import Enum


class WeatherCondition(Enum):
    CLEAR = 1
    FAIR = 2
    CLOUDY = 3
    OVERCAST = 4
    FOG = 5
    FREEZING_FOG = 6
    LIGHT_RAIN = 7
    RAIN = 8
    HEAVY_RAIN = 9
    FREEZING_RAIN = 10
    HEAVY_FREEZING_RAIN = 11
    SLEET = 12
    HEAVY_SLEET = 13
    LIGHT_SNOWFALL = 14
    SNOWFALL = 15
    HEAVY_SNOWFALL = 16
    RAIN_SHOWER = 17
    HEAVY_RAIN_SHOWER = 18
    SLEET_SHOWER = 19
    HEAVY_SLEET_SHOWER = 20
    SNOW_SHOWER = 21
    HEAVY_SNOW_SHOWER = 22
    LIGHTNING = 23
    HAIL = 24
    THUNDERSTORM = 25
    HEAVY_THUNDERSTORM = 26
    STORM = 27


weather_condition_descriptions: dict[WeatherCondition, str] = {
    WeatherCondition.CLEAR: "A bright, sunny day with no visible clouds in the sky. "
                            "Vibrant lighting and sharp shadows dominate.",
    WeatherCondition.FAIR: "Mostly sunny conditions with a few scattered, "
                           "fluffy clouds in the sky. Bright overall, "
                           "but some diffuse lighting.",
    WeatherCondition.CLOUDY: "The sky is covered with a mix of white and grey clouds, "
                             "with occasional patches of blue visible. "
                             "Soft shadows are present.",
    WeatherCondition.OVERCAST: "A uniformly grey sky with complete cloud cover, "
                               "diffused light, and no visible shadows.",
    WeatherCondition.FOG: "A dense, white, or grey mist that obscures visibility, "
                          "softening all background details and creating a muted "
                          "atmosphere.",
    WeatherCondition.FREEZING_FOG: "Similar to regular fog, but with frosty particles "
                                   "on surfaces like trees, cars, and grass, "
                                   "often giving a shiny, icy appearance.",
    WeatherCondition.LIGHT_RAIN: "A gentle drizzle, with fine raindrops visible and "
                                 "light wetness on surfaces. Overcast skies with "
                                 "occasional small puddles.",
    WeatherCondition.RAIN: "Steady rainfall, with visible raindrops, wet roads, "
                           "puddles, and overcast skies. Surface reflections may be "
                           "more pronounced.",
    WeatherCondition.HEAVY_RAIN: "Intense rainfall with large, fast-falling droplets. "
                                 "Poor visibility and substantial water accumulation "
                                 "on the ground.",
    WeatherCondition.FREEZING_RAIN: "Rainfall that freezes on contact, creating a "
                                    "shiny, icy coating on roads, trees, and other "
                                    "surfaces.",
    WeatherCondition.HEAVY_FREEZING_RAIN: "Intense freezing rain, with thick ice "
                                          "accumulation on surfaces, often weighing "
                                          "down tree branches and power lines.",
    WeatherCondition.SLEET: "Small, partially frozen pellets falling from the sky. "
                            "Ground may have a slushy appearance.",
    WeatherCondition.HEAVY_SLEET: "A large volume of sleet falling, covering the "
                                  "ground with a noticeable, crunchy layer.",
    WeatherCondition.LIGHT_SNOWFALL: "Gentle, sparse snowflakes drifting down, "
                                     "lightly dusting surfaces. Often creates a calm, "
                                     "serene setting.",
    WeatherCondition.SNOWFALL: "Steady, moderate snow falling, covering the ground "
                               "and trees with a consistent layer of white.",
    WeatherCondition.HEAVY_SNOWFALL: "Thick, fast-falling snowflakes, quickly "
                                     "accumulating on the ground and reducing "
                                     "visibility.",
    WeatherCondition.RAIN_SHOWER: "Brief but noticeable rain with visible raindrops "
                                  "and sudden wetness on surfaces. Often with a "
                                  "dynamic sky, including breaks of sunlight.",
    WeatherCondition.HEAVY_RAIN_SHOWER: "A sudden, intense burst of rain with large "
                                        "drops and heavy ground wetness, often "
                                        "accompanied by dark clouds.",
    WeatherCondition.SLEET_SHOWER: "A brief, localized fall of sleet, creating patches "
                                   "of slushy ground and visible frozen pellets.",
    WeatherCondition.HEAVY_SLEET_SHOWER: "A sudden, heavy burst of sleet, quickly "
                                         "covering the ground in icy pellets and "
                                         "making surfaces slippery.",
    WeatherCondition.SNOW_SHOWER: "A short burst of light to moderate snow, creating "
                                  "a temporary dusting of white on the ground.",
    WeatherCondition.HEAVY_SNOW_SHOWER: "A sudden, intense flurry of snow, reducing "
                                        "visibility and quickly accumulating on "
                                        "surfaces.",
    WeatherCondition.LIGHTNING: "Bright, sharp flashes of light in the sky, often "
                                "against a dark or stormy backdrop, with occasional "
                                "bolts visible.",
    WeatherCondition.HAIL: "Small, hard pellets or larger chunks of ice falling from "
                           "the sky, often bouncing upon impact with the ground or "
                           "surfaces.",
    WeatherCondition.THUNDERSTORM: "Dark, stormy skies with flashes of lightning, "
                                   "rumbles of thunder, and rain. Often includes "
                                   "dynamic cloud formations.",
    WeatherCondition.HEAVY_THUNDERSTORM: "A violent storm with frequent lightning, "
                                         "loud thunder, heavy rain, and occasionally "
                                         "hail or strong winds.",
    WeatherCondition.STORM: "Extreme weather with strong winds, heavy precipitation, "
                            "and dramatic skies. Can include rain, snow, or hail, "
                            "often with low visibility.",
}
