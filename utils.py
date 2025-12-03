def calculate_daily_goal(weight, age):
    """
    Calculate daily water intake goal based on weight and age.
    Simple formula: 
    - < 30 years: weight * 40
    - 30-55 years: weight * 35
    - > 55 years: weight * 30
    """
    if age < 30:
        return int(weight * 40)
    elif age <= 55:
        return int(weight * 35)
    else:
        return int(weight * 30)
