def drop_bad_predictors(X):
    medic_deaths_cols = [col for col in X.columns if col.endswith("medic_deaths") #Drop Demo Medic Deaths
                        or "medic_medic_deaths" in col  # Drop medic_medic_draths columns that keep coming up
                        or "_medic_deaths_" in col] # Drop medic deaths for scout and demo

    medic_kda_cols = [col for col in X.columns if col.startswith("medic") and
                    "kills" in col and
                    "kdapd" in col]
    X.drop(medic_kda_cols,axis =1,inplace = True)

    #X.drop(unimportant_columns,axis =1, inplace = True)

    X.drop(medic_deaths_cols,axis = 1, inplace = True)

    class_kda_drop = [col for col in X.columns if "class_kda" in col and "pd" not in col]

    X.drop(class_kda_drop,axis =1, inplace = True)

    return X
