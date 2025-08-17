import pandas as pd
def drop_bad_predictors(X):

    medic_deaths_cols = [col for col in X.columns if col.endswith("medic_deaths") #Drop Demo Medic Deaths
                        or "medic_medic_deaths" in col  # Drop medic_medic_draths columns that keep coming up
                        or "_medic_deaths_" in col] # Drop medic deaths for scout and demo

    medic_kda_cols = [col for col in X.columns if col.startswith("medic") and
                    "kills" in col and
                    "kdapd" in col]
    unnamed_cols = [col for col in X.columns if 'Unnamed' in col] # Drop any columns that are an index from another dataset

    class_kda_drop = [col for col in X.columns if "class_kda" in col and "pd" not in col] #Drop all non normalized class kda columns

    class_kda_assists_cols = [
        col for col in X.columns
        if "class_kda" in col
        and "assist" in col
        and not col.startswith("medic")
    ] # Drop all class assists cols that dont start with medic due to high correlation

    drop_cols = (
        medic_deaths_cols + 
        medic_kda_cols + 
        unnamed_cols + 
        class_kda_drop + 
        class_kda_assists_cols
    )
    drop_cols = pd.Series(drop_cols).unique()
    drop_cols = list(drop_cols)

    X.drop(drop_cols,axis = 1, inplace = True)
    
    return X
