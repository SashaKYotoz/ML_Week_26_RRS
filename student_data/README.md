# Coffee Recipe Recommendation Challenge - Student Dataset

## Overview

Dataset for building a coffee recipe recommendation system.

## Data Files


### `recipes.csv`
| Column | Type | Description |
|--------|------|-------------|
| recipe_id | string | Unique identifier (e.g., "recipe_espresso_000") |
| name | string | Recipe name |
| description | string | Recipe description |
| taste_bitterness | float | Bitterness level (0.0-1.0) |
| taste_sweetness | float | Sweetness level (0.0-1.0) |
| taste_acidity | float | Acidity level (0.0-1.0) |
| taste_body | float | Body/richness level (0.0-1.0) |
| strength | int | Caffeine strength (1-5) |
| portion_size_ml | int | Serving size in milliliters |
| preparation_time_minutes | int | Time to prepare |
| difficulty | string | "beginner", "intermediate", or "advanced" |
| required_equipment | JSON array | Equipment needed (e.g., `["espresso_machine", "grinder"]`) |
| required_products | JSON object | Ingredients with amounts (e.g., `{"coffee_beans": "18g"}`) |
| tags | JSON array | Recipe tags (e.g., `["hot", "classic", "quick"]`) |

### `users.csv`
| Column | Type | Description |
|--------|------|-------------|
| user_id | string | Unique identifier (e.g., "user_00000") |
| username | string | Display name |
| owned_equipment | JSON array | Equipment user owns |
| available_products | JSON array | Products user has access to |
| taste_pref_bitterness | float | Preference for bitterness (0.0-1.0) |
| taste_pref_sweetness | float | Preference for sweetness (0.0-1.0) |
| taste_pref_acidity | float | Preference for acidity (0.0-1.0) |
| taste_pref_body | float | Preference for body (0.0-1.0) |
| preferred_strength | int | Preferred caffeine strength (1-5) |
| preferred_portion_size | string | "small", "medium", or "large" |
| dietary_restrictions | JSON array | Dietary constraints |
| account_created | timestamp | Account creation date |

### `interactions_train.csv`
| Column | Type | Description |
|--------|------|-------------|
| interaction_id | string | Unique identifier |
| user_id | string | Reference to users.csv |
| recipe_id | string | Reference to recipes.csv |
| timestamp | ISO 8601 | When interaction occurred |
| rating | float (nullable) | User rating (1.0-5.0), may be missing |
| completed | bool | Whether preparation was completed |

### `interactions_val.csv`
Validation set for warm users (same schema as interactions_train.csv).

### `interactions_val_cold.csv`
Validation set for cold-start users (same schema).

### `cold_users.json`
JSON array of user_ids that have zero interactions in training data.

---

## Evaluation Script Signature

Your submission must implement this function:

```python
from typing import List, Tuple
import pandas as pd

def recommend(
    user_id: str,
    users_df: pd.DataFrame,
    recipes_df: pd.DataFrame,
    train_df: pd.DataFrame,
    n: int = 5
) -> List[Tuple[str, float]]:
    """
    Generate top-N recipe recommendations for a user.

    Args:
        user_id: Target user identifier
        users_df: Users dataframe (users.csv loaded)
        recipes_df: Recipes dataframe (recipes.csv loaded)
        train_df: Training interactions (interactions_train.csv loaded)
        n: Number of recommendations to return

    Returns:
        List of (recipe_id, score) tuples, sorted by score descending.
        Higher scores indicate stronger recommendations.

    Example:
        >>> recommend("user_00000", users_df, recipes_df, train_df, n=5)
        [
            ("recipe_espresso_000", 4.85),
            ("recipe_americano_002", 4.72),
            ("recipe_latte_005", 4.65),
            ("recipe_cappuccino_004", 4.51),
            ("recipe_mocha_009", 4.33)
        ]
    """
    pass
```

### Requirements

1. **Equipment filtering**: Only recommend recipes where `required_equipment` is a subset of user's `owned_equipment`
2. **Return format**: List of tuples `(recipe_id: str, score: float)`
3. **Score ordering**: Higher scores = better recommendations
4. **Handle cold-start**: Function must work for users with no training history

### Evaluation Metric

**NDCG@5** (Normalized Discounted Cumulative Gain at 5):

```python
def ndcg_at_k(relevances: List[float], k: int) -> float:
    relevances = relevances[:k]
    dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances))
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevances))
    return dcg / idcg if idcg > 0 else 0.0
```

Relevance for each recommendation is computed as:
- `rating / 5.0` if user rated the recipe in validation set
- `0.0` if recipe was not rated

---

## Important Notes

1. **Cold-start users**: 300 users have zero training interactions. Your model must handle these users using profile features only.

2. **Missing ratings**: Not all interactions have ratings. Use `completed` field and interaction frequency as implicit feedback.

3. **Temporal patterns**: Timestamps contain valuable information about user behavior patterns.

4. **Equipment constraints**: A recommendation is invalid if user doesn't own required equipment.
