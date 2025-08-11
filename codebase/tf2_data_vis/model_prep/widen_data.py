def widen_data(medic_players,combat_players):
    index_columns = ['id', 'team', 'primary_class']
    combat_wide = (
        combat_players
        .set_index(index_columns)  # MultiIndex
        .unstack('primary_class')                    # Pivot on class
    )

    medic_wide = (
        medic_players
        .set_index(index_columns)  # MultiIndex
        .unstack('primary_class')                        # Pivot on class
    )

    # Step 3: Flatten the MultiIndex column names
    combat_wide.columns = [f"{cls}_{stat}" for stat, cls in combat_wide.columns]

    # Step 4: Reset index
    combat_wide = combat_wide.reset_index()

    # Drop non-scout offclass 
    cols = [col for col in combat_wide.columns if 'offclass' in col and 'scout' not in col]
    combat_wide = combat_wide.drop(cols,axis = 1)

    # Step 3: Flatten the MultiIndex column names
    medic_wide.columns = [f"{cls}_{stat}" for stat, cls in medic_wide.columns]

    # Step 4: Reset index
    medic_wide = medic_wide.reset_index()

    return medic_wide,combat_wide