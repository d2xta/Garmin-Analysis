

def build_hierarchical_r2_table(df):
    styler = (
        df.style
        .hide(axis="index")
        .format({
            "Duration R²": "{:.1%}",
            "Bedtime +ΔR²": "{:.1%}",
            "Quadratic +ΔR²": "{:.1%}",
            "Interaction +ΔR²": "{:.1%}",
            "Total R²": "{:.1%}",
            "Bedtime p": "{:.4f}",
            "Quadratic p": "{:.4f}",
            "Interaction p": "{:.4f}"
        })
        .set_table_styles([
            {"selector": "table", "props": [
                ("border-collapse", "collapse"),
                ("margin", "10px 0"),
                ("font-size", "12px"),
                ("max-width", "700px"),
                ("table-layout", "fixed"),
            ]},
            {"selector": "th", "props": [
                ("border", "1px solid black"),
                ("padding", "4px"),
                ("text-align", "center"),
                ("word-wrap", "break-word"),
            ]},
            {"selector": "td", "props": [
                ("border", "1px solid black"),
                ("padding", "4px"),
                ("text-align", "center"),
                ("word-wrap", "break-word"),
            ]},
        ])
    )

    return styler
