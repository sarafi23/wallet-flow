:: Fix dashboard template
@echo off
docker compose exec web bash -c "sed -i '666,669d' /app/finance/templates/finance/dashboard.html"
docker compose exec web bash -c "sed -i '665a\                                    <div style=\"font-size: 2.5rem; font-weight: 700; color: {{ health_color }};\">{{ health_score }}%</div>\n\                                    <div style=\"font-size: 0.875rem; color: var(--text-muted);\">{{ health_status }}</div>' /app/finance/templates/finance/dashboard.html"
echo Template fixed!
