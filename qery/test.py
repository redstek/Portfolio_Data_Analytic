import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="123",
    database="skyeng_db"
)

query = """
with first_payments as
    (
    select 
            user_id
        ,   date_trunc ('day', min (transaction_datetime)) as first_payment_date
    from skyeng_db.payments
    where status_name = 'success'
    group by user_id
    )

,

all_dates as 
    (
    select 
            distinct date_trunc ('day', class_start_datetime) as dt
    from skyeng_db.classes
    where date_trunc ('year',class_start_datetime) = '2016-01-01'
    )

,

payments_by_dates as
    (
    select 
            user_id
        ,   date_trunc ('day', transaction_datetime) as payment_day
        ,   sum (classes) as transaction_balance_change
        from skyeng_db.payments
    where status_name = 'success'
    group by user_id, payment_day
    )
,

all_dates_by_user as 
    (
    select 
            user_id
        ,   dt
    from first_payments as p
        join all_dates as d
            on d.dt >= p.first_payment_date
    )
,

classes_by_dates as
    (
    select 
            user_id
        ,   date_trunc ('day', class_start_datetime) as class_date
        ,   count (*) *(-1) as classes
    from skyeng_db.classes
    where (class_status = 'success' or class_status = 'failed_by_student')
            and class_type != 'trial'
    group by user_id, class_date
    )

,

payments_by_dates_cumsum as
    (
    select 
            du.user_id
        ,   dt
        ,   coalesce (transaction_balance_change, 0) as transaction_balance_change
        ,   coalesce (sum (transaction_balance_change) over (partition by du.user_id order by dt), 0) as transaction_balance_change_cs
    from all_dates_by_user as du
        left join payments_by_dates as pd
            on du.user_id = pd.user_id and du.dt = pd.payment_day
    )

,

classes_by_dates_dates_cumsum as
    (
    select 
            du.user_id
        ,   dt
        ,   coalesce (classes, 0) as classes
        ,   coalesce (sum (classes) over (partition by du.user_id order by dt), 0) as classes_cs
    from all_dates_by_user as du
        left join classes_by_dates as cd
            on du.user_id = cd.user_id and du.dt = cd.class_date
     
    )

,

balances as
    (
    select 
            cd.user_id
        ,   cd.dt
        ,   transaction_balance_change
        ,   transaction_balance_change_cs
        ,   classes
        ,   classes_cs
        ,   (classes_cs + transaction_balance_change_cs) as balance
    from payments_by_dates_cumsum as pd
            join classes_by_dates_dates_cumsum as cd
                on pd.user_id = cd.user_id and pd.dt = cd.dt
    )
select 
        dt
    ,   sum (transaction_balance_change) as transaction_balance_change_sum
    ,   sum (transaction_balance_change_cs) as transaction_balance_change_cs_sum
    ,   sum (classes) as classes_sum
    ,   sum (classes_cs) as classes_cs_sum
    ,   sum (balance)  as balance_sum
from balances
group by dt
order by dt
"""
df = pd.read_sql(query, conn)

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(df['dt'], df['transaction_balance_change_sum'], label='Transaction Balance Change')
ax.plot(df['dt'], df['transaction_balance_change_cs_sum'], label='Transaction Balance Change Cumulative Sum')
ax.plot(df['dt'], df['classes_sum'], label='Classes')
ax.plot(df['dt'], df['classes_cs_sum'], label='Classes Cumulative Sum')
ax.plot(df['dt'], df['balance_sum'], label='Balance')

ax.set_xlabel('Date')
ax.set_ylabel('Value')
ax.set_title('Graph')
ax.legend()

plt.show()