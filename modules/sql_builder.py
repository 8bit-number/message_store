import time


# lst here is a list of author_id


def find_agent(lst):
    """
    Searches if authors already in agent and returns agent id or NULL otherwise
    :param lst: list of author_id
    :return: agent_id
    """
    query = """
(select agent.id from agent
inner join author_agent on (agent.id = author_agent.group_id)
where author_agent.author_id = {}
group by agent.id)
""".format(lst[0])
    for i in range(1, len(lst)):
        query += """intersect"""
        query += """
(select agent.id from agent
inner join author_agent on (agent.id = author_agent.group_id)
where author_agent.author_id = {}
group by agent.id)
""".format(lst[i])
    query += """limit 1"""
    return query


# print(find_agent([30, 31, 32]))

def create_agent(lst):
    """
    Creates an agent from authors and returns agent id
    :param lst: list of author_id
    :return: agent_id
    """
    name = str(time.time())
    query = """
INSERT INTO agent(name) VALUES ('{}');
""".format(name)
    for i in lst:
        query += """
WITH idi AS (
SELECT id FROM agent
WHERE name = '{}'
)
""".format(name)
        query += """INSERT INTO author_agent(group_id,author_id) VALUES ((select * from idi),{});
""".format(i)
    query += """
SELECT id FROM agent
WHERE name = '{}'
""".format(name)
    return query


# print(create_agent([30, 31, 32]))


def get_price(lst, style_id):
    """
    Takes list of author_id and style_id and calculates the average price for group considering discounts
    :param lst: list of author_id
    :param style_id: style_id
    :return: price_per_1000
    """
    query = """
select sum(price_per_1000)/{} as price_per_1000 from
(""".format(len(lst))
    subquery = """
(select
CASE
    WHEN discount.sale_to >= CURRENT_DATE and discount.style_id = {} THEN author.price_per_1000 * discount.discount
    ELSE author.price_per_1000
END
from author
left join discount on (author.id = discount.author_id)
where author.id = {})
""".format(style_id, lst[0])
    for i in range(1, len(lst)):
        subquery += """union all"""
        subquery += """
(select
CASE
    WHEN discount.sale_to >= CURRENT_DATE and discount.style_id = {} THEN author.price_per_1000 * discount.discount
    ELSE author.price_per_1000
END
from author
left join discount on (author.id = discount.author_id)
where author.id = {})
""".format(style_id, lst[i])
    query += subquery
    query += """)as s"""
    return query


# print(get_price([30, 31, 32], 1))


def create_order(account_id, principal_id, agent_id, style_id, average_price, volume):
    """
    Take all inputs, creates empty post and order
    :param account_id: account_id
    :param principal_id: principal_id
    :param agent_id: agent_id
    :param style_id: style_id
    :param average_price: average_price from get_price()
    :param volume: volume
    :return: creates post and order
    """
    price = volume / 1000 * average_price
    query = """
INSERT INTO posts(account_id, text, style_id, date) VALUES ({}, '', {}, CURRENT_DATE);
WITH idi AS (
SELECT max(id) from posts)
""".format(account_id, style_id)
    query += """
INSERT INTO orders(principal_id, agent_id, volume, post_id, price, date, status) VALUES ({}, {}, {}, (select * from idi), {}, CURRENT_DATE, 'opened');
""".format(principal_id, agent_id, volume, price)
    return query


# print(create_order(1, 1, 1, 1, 400, 1000))

def create_account(principal_id, social_network_id, login, password):
    """
    Takes all inputs, adds user account in social network.
    :param principal_id: principal_id
    :param social_network_id: social_network_id
    :param login : login
    :param password : password
    :return: creates account
    """
    query = """
    INSERT INTO account(principal_id, social_network_id, login, password) 
    VALUES ({},{},'{}','{}');
    """.format(principal_id, social_network_id, login, password)
    return query


def add_account(name, login, password, author):
    """
    Creates an account for author
    :param name:
    :param login:
    :param password:
    :param author:
    :return:
    """
    if author == 1:
        query = f"""
            insert into authentication(login, password, author)
            values ('{login}', '{password}', true);

            INSERT INTO author(id, name, price_per_1000, active)
            VALUES ((select id from authentication
            where login = '{login}'
            and password = '{password}' 
            and author = true),  '{name}', 500, FALSE);
            """
    else:
        query = f"""
            insert into authentication(login, password, author)
            values ('{login}', '{password}', false);

            INSERT INTO principal(id, name)
            VALUES ((select id from authentication
            where login = '{login}'
            and password = '{password}' 
            and author = false),  '{name}');
            """

    return query


def general_discount(author_id, sale_to, discount):
    """
    Discount for all the styles
    :param author_id:
    :param sale_to:
    :param discount:
    :return:
    """
    query = \
        f"""
       insert into discount(author_id, style_id, sale_to, discount)
       values
       ({author_id}, 1, cast({sale_to} as date), {discount}),
       ({author_id}, 2, cast({sale_to} as date), {discount}),
       ({author_id}, 3, cast({sale_to} as date), {discount}),
       ({author_id}, 4, cast({sale_to} as date), {discount}),
       ({author_id}, 5, cast({sale_to} as date), {discount}),
       ({author_id}, 6, cast({sale_to} as date), {discount}),
       ({author_id}, 7, cast({sale_to} as date), {discount}),
       ({author_id}, 8, cast({sale_to} as date), {discount}),
       ({author_id}, 9, cast({sale_to} as date), {discount}),    
       ({author_id}, 10, cast({sale_to} as date), {discount}),
       ({author_id}, 11, cast({sale_to} as date), {discount}),
       ({author_id}, 12, cast({sale_to} as date), {discount}),
       ({author_id}, 13, cast({sale_to} as date), {discount});
       """
    return query