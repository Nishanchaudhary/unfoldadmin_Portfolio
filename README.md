###Django Database Query Optimization – Production Guide
https://img.shields.io/badge/Django-5.2.6-092E20?style=flat&logo=django&logoColor=white
https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white
https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat&logo=postgresql&logoColor=white
https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql&logoColor=white
https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/version-2.0.0-blue.svg
https://img.shields.io/badge/PRs-welcome-brightgreen.svg
https://img.shields.io/badge/contributions-welcome-orange.svg

A comprehensive production-ready guide to Django ORM optimization techniques, performance tuning, and database best practices. This guide covers essential patterns, common pitfalls, and advanced strategies to build scalable, high-performance Django applications.

Author: Nishan Kumar Chaudhary
GitHub: @Nishanchaudhary
Live Demo: bginfotechs.com.np

📋 Table of Contents
✨ Key Features

📚 Core Optimization Techniques

1️⃣ Avoid the N+1 Query Problem

2️⃣ Optimize ManyToMany & Reverse Relations

3️⃣ Never Use .all() Blindly in Production

4️⃣ Fetch Only Required Fields

5️⃣ Use exists() Instead of count()

6️⃣ Use Bulk Operations for Insert & Update

7️⃣ Always Use Database Indexing

8️⃣ Avoid Queries Inside Loops

9️⃣ Use Database Aggregation Instead of Python Logic

🔟 Avoid len(queryset)

🚀 Advanced Production Optimization Rules

📊 Query Analysis & Debugging

⚠️ Common Mistakes That Cause Performance Issues

🎯 Golden Rules for Production Django

📈 Performance Testing & Monitoring

⚙️ Installation & Setup

📝 Contributing

📄 License

📞 Contact

✨ Key Features
🎯 Core Optimization Techniques
N+1 Query Prevention – Master select_related() and prefetch_related()

Memory Optimization – Efficient data loading with only(), defer(), and values()

Bulk Operations – Batch inserts/updates with bulk_create() and bulk_update()

Database Indexing – Strategic indexing for frequently queried fields

Query Analysis – Built-in debugging tools and query profiling

🛠️ Advanced Features
Connection Pooling – Persistent database connections for reduced overhead

Query Caching – Redis/Memcached integration for expensive queries

Materialized Views – Pre-computed aggregates for complex reports

Table Partitioning – Scale large tables with date-based partitioning

Raw SQL Support – Fallback to optimized raw queries when needed

📊 Monitoring & Debugging
Django Debug Toolbar – Real-time query inspection

Custom Query Logger – Slow query detection and logging

Performance Middleware – Request/response timing and query counting

EXPLAIN Analysis – Query execution plan visualization

📚 Core Optimization Techniques
1️⃣ Avoid the N+1 Query Problem (MOST IMPORTANT)
The N+1 query problem occurs when your code executes one query to fetch parent records and then N additional queries to fetch related data for each parent record.

❌ BAD CODE (N+1 Problem)
python
posts = Post.objects.all()

for post in posts:  # 1 query for posts
    print(post.author.username)  # N queries for authors
📊 What Happens Internally
sql
-- Query 1: Fetch all posts
SELECT * FROM posts;

-- Query 2: Fetch author for post 1
SELECT * FROM users WHERE id = 1;

-- Query 3: Fetch author for post 2
SELECT * FROM users WHERE id = 2;

-- ... and so on for N posts
Total = 1 + N queries – This kills performance on admin dashboards and APIs.

✅ OPTIMIZED GOOD CODE
python
# Solution 1: Using select_related for ForeignKey/OneToOne
posts = Post.objects.select_related('author')

for post in posts:  # Only 1 query with JOIN
    print(post.author.username)
📊 Optimized SQL
sql
-- Single query with JOIN
SELECT posts.*, users.* 
FROM posts 
INNER JOIN users ON posts.author_id = users.id;
📌 Rule
Always use select_related() for ForeignKey and OneToOneField relationships

2️⃣ Optimize ManyToMany & Reverse Relations (prefetch_related)
For ManyToMany fields and reverse ForeignKey relationships, select_related() won't work. Use prefetch_related() instead.

❌ BAD CODE
python
posts = Post.objects.all()

for post in posts:  # 1 query for posts
    tags = post.tags.all()  # N queries for tags
✅ OPTIMIZED GOOD CODE
python
from django.db.models import Prefetch

# Basic prefetch
posts = Post.objects.prefetch_related('tags')

for post in posts:  # Only 2 queries total!
    tags = post.tags.all()
🚀 Advanced Prefetch Techniques
python
# Prefetch with filters
posts = Post.objects.prefetch_related(
    Prefetch('comments', 
             queryset=Comment.objects.filter(is_approved=True),
             to_attr='approved_comments')
)

# Multiple prefetches
posts = Post.objects.prefetch_related(
    'tags',
    'comments__author',  # Nested prefetch
)

# Prefetch with custom ordering
from django.db.models import Prefetch

posts = Post.objects.prefetch_related(
    Prefetch('comments', 
             queryset=Comment.objects.order_by('-created_at')[:5],
             to_attr='recent_comments')
)
📌 Rule
Use prefetch_related() for ManyToMany fields and reverse ForeignKey relationships

3️⃣ Never Use .all() Blindly in Production
Using .all() without filters can load entire tables into memory, causing performance degradation and potential crashes.

❌ BAD CODE
python
# Loads entire users table into memory
users = User.objects.all()  

# Even worse - processing in memory
for user in users:
    process_user(user)
✅ OPTIMIZED GOOD CODE
python
# Always filter when possible
users = User.objects.filter(is_active=True)

# Use iterator for large datasets
for user in User.objects.filter(is_active=True).iterator(chunk_size=1000):
    process_user(user)

# Paginate results
from django.core.paginator import Paginator

users = User.objects.filter(is_active=True)
paginator = Paginator(users, 100)  # 100 users per page
page_users = paginator.get_page(1)
📌 Rule
.all() is only safe for small, controlled tables (lookup tables, configurations)

Always add filters for production queries

Use iterator() for memory-efficient processing of large datasets

4️⃣ Fetch Only Required Fields (only, values, values_list)
Loading unnecessary columns wastes memory and network bandwidth.

❌ BAD CODE
python
# Loads all columns (password, permissions, etc.)
users = User.objects.all()
✅ OPTIMIZED GOOD CODE (Multiple Approaches)
python
# Approach 1: Model instances with only specific fields
users = User.objects.only('id', 'username', 'email')

# Approach 2: Exclude specific fields
users = User.objects.defer('password', 'last_login')

# Approach 3: Dictionary results (lightweight)
users = User.objects.values('id', 'username', 'email')

# Approach 4: Flat list of values
user_ids = User.objects.values_list('id', flat=True)

# Approach 5: Named tuples
from django.db.models import Value
users = User.objects.values_list('username', 'email', named=True)

# Approach 6: For complex queries with annotations
from django.db.models import F, Count
users = User.objects.annotate(
    post_count=Count('posts')
).values('id', 'username', 'post_count')
📊 Performance Comparison
python
import tracemalloc

tracemalloc.start()
users = list(User.objects.all())  # Memory: 50MB
current, peak = tracemalloc.get_traced_memory()
print(f"All fields: {peak / 1024 / 1024:.2f} MB")

tracemalloc.clear_traces()
users = list(User.objects.only('id', 'username'))  # Memory: 5MB
current, peak = tracemalloc.get_traced_memory()
print(f"Only required: {peak / 1024 / 1024:.2f} MB")
📌 Rule
Use .values() or .only() to limit fetched columns, especially for APIs and dashboards

5️⃣ Use exists() Instead of count()
When checking for existence, exists() is significantly faster than count().

❌ BAD CODE
python
# Counts all matching rows unnecessarily
if User.objects.filter(email=email).count() > 0:
    send_welcome_email()

# Even worse
if len(User.objects.filter(email=email)) > 0:
    send_welcome_email()
✅ OPTIMIZED GOOD CODE
python
# Stops at first match - much faster
if User.objects.filter(email=email).exists():
    send_welcome_email()

# For complex conditions
from django.db.models import Q

if User.objects.filter(
    Q(email=email) | Q(username=username)
).exists():
    handle_duplicate()
📊 SQL Comparison
sql
-- count() executes:
SELECT COUNT(*) FROM users WHERE email = 'test@example.com';

-- exists() executes:
SELECT (1) AS "a" FROM users WHERE email = 'test@example.com' LIMIT 1;
📌 Rule
Use .exists() for existence checks, not .count() > 0

6️⃣ Use Bulk Operations for Insert & Update
Loop-based inserts/updates create N+1 query problems for write operations.

❌ BAD CODE
python
# Executes 1 query per row
users = []
for i in range(1000):
    User.objects.create(
        username=f'user{i}',
        email=f'user{i}@example.com'
    )
✅ OPTIMIZED GOOD CODE
python
# Bulk create - single query
users = [
    User(username=f'user{i}', email=f'user{i}@example.com')
    for i in range(1000)
]
User.objects.bulk_create(users, batch_size=500)

# Bulk update
users = User.objects.filter(is_active=True)
for user in users:
    user.last_login = timezone.now()

User.objects.bulk_update(users, ['last_login'], batch_size=500)

# Bulk update with different values
users_data = [
    User(id=1, username='new_name1'),
    User(id=2, username='new_name2'),
]
User.objects.bulk_update(users_data, ['username'])

# Bulk delete (raw SQL - use carefully)
User.objects.filter(last_login__lt=cutoff_date).delete()

# Bulk create with related objects
posts = []
for i in range(100):
    posts.append(Post(title=f'Post {i}', author=author))

Post.objects.bulk_create(posts)
📊 Performance Comparison
python
import time

# Bad approach
start = time.time()
for i in range(100):
    User.objects.create(username=f'test{i}')
print(f"Loop: {time.time() - start:.2f}s")  # ~2.5 seconds

# Good approach
start = time.time()
users = [User(username=f'test{i}') for i in range(100)]
User.objects.bulk_create(users)
print(f"Bulk: {time.time() - start:.2f}s")  # ~0.05 seconds (50x faster)
📌 Rule
Never save objects inside loops - use bulk operations for batch inserts/updates

7️⃣ Always Use Database Indexing
Proper indexing is crucial for query performance, especially on large tables.

❌ BAD MODEL
python
class User(models.Model):
    email = models.EmailField()  # No index
    last_login = models.DateTimeField()  # Frequently filtered, no index
    status = models.CharField(max_length=20)  # Used in filters, no index
✅ OPTIMIZED MODEL
python
class User(models.Model):
    # Single field indexes
    email = models.EmailField(
        unique=True,  # Implicitly creates index
        db_index=True  # Explicit index
    )
    
    last_login = models.DateTimeField(
        db_index=True  # Index for range queries
    )
    
    status = models.CharField(
        max_length=20,
        db_index=True  # Index for equality filters
    )
    
    class Meta:
        indexes = [
            # Composite index for common query patterns
            models.Index(fields=['status', 'last_login']),
            
            # Partial index (PostgreSQL)
            models.Index(
                condition=Q(is_active=True),
                fields=['email'],
                name='active_user_email_idx'
            ),
            
            # Functional index (PostgreSQL)
            models.Index(
                F('last_login_date'),  # Custom expression
                name='last_login_date_idx'
            ),
        ]
🎯 When to Add Indexes
python
# Index fields used in:
# 1. WHERE clauses
User.objects.filter(email='test@example.com')  # Index on email

# 2. JOIN conditions
Post.objects.filter(author=user)  # ForeignKey automatically indexed

# 3. ORDER BY clauses
User.objects.order_by('-last_login')  # Index on last_login

# 4. GROUP BY clauses
User.objects.values('status').annotate(count=Count('id'))  # Index on status

# 5. DISTINCT operations
User.objects.distinct('status')  # Index on status
📌 Rule
Index fields used in filter(), get(), order_by(), and distinct() operations

8️⃣ Avoid Queries Inside Loops
Querying inside loops is a common source of N+1 query problems.

❌ BAD CODE
python
# N+1 queries
orders = Order.objects.all()
for order in orders:
    product = Product.objects.get(id=order.product_id)  # N queries
    print(f"{order.id}: {product.name}")
✅ OPTIMIZED GOOD CODE
python
# Solution 1: Use select_related/prefetch_related
orders = Order.objects.select_related('product')
for order in orders:  # Single query with JOIN
    print(f"{order.id}: {order.product.name}")

# Solution 2: Batch fetch for complex cases
order_ids = [order.product_id for order in orders]
products = Product.objects.filter(id__in=order_ids).in_bulk()
# products is {id: product}

for order in orders:
    product = products.get(order.product_id)
    print(f"{order.id}: {product.name if product else 'Unknown'}")

# Solution 3: Using subqueries for complex filtering
from django.db.models import Subquery, OuterRef

recent_products = Product.objects.filter(
    category=OuterRef('category')
).order_by('-created_at')[:1]

orders = Order.objects.annotate(
    recent_product=Subquery(recent_products.values('name'))
)
📌 Rule
Query once, reuse data - never put database queries inside loops

9️⃣ Use Database Aggregation Instead of Python Logic
Let the database do what it's optimized for - aggregations and calculations.

❌ BAD CODE
python
# Inefficient Python aggregation
total = 0
for order in Order.objects.all():
    total += order.price

average = total / Order.objects.count()

# Even worse - processing in Python
expensive_orders = []
for order in Order.objects.all():
    if order.price > 1000:
        expensive_orders.append(order)
✅ OPTIMIZED GOOD CODE
python
from django.db.models import Sum, Avg, Count, Max, Min, Q, F

# Basic aggregations
stats = Order.objects.aggregate(
    total=Sum('price'),
    average=Avg('price'),
    max_price=Max('price'),
    min_price=Min('price'),
    order_count=Count('id')
)

# Conditional aggregations
stats = Order.objects.aggregate(
    paid_count=Count('id', filter=Q(status='paid')),
    pending_count=Count('id', filter=Q(status='pending')),
    total_revenue=Sum('price', filter=Q(status='paid'))
)

# Annotate each object with aggregated data
users = User.objects.annotate(
    order_count=Count('orders'),
    total_spent=Sum('orders__price'),
    avg_order=Avg('orders__price'),
    last_order=Max('orders__created_at')
).filter(order_count__gt=0)

# Group by with multiple aggregations
stats_by_status = Order.objects.values('status').annotate(
    count=Count('id'),
    total=Sum('price'),
    average=Avg('price')
).order_by('status')

# Complex aggregations with F expressions
from django.db.models import F, FloatField, ExpressionWrapper

orders = Order.objects.annotate(
    tax=F('price') * 0.1,
    total_with_tax=F('price') * 1.1,
    profit_margin=ExpressionWrapper(
        (F('price') - F('cost')) / F('price') * 100,
        output_field=FloatField()
    )
)
📌 Rule
Always aggregate in the database, not in Python code

🔟 Avoid len(queryset)
Using len(queryset) evaluates the entire queryset and loads all objects into memory.

❌ BAD CODE
python
# Loads all users into memory
user_count = len(User.objects.all())

# Even worse - checks existence with len
if len(User.objects.filter(email=email)) > 0:
    send_email()
✅ OPTIMIZED GOOD CODE
python
# Use count() for counting
user_count = User.objects.count()

# Use exists() for existence checks
if User.objects.filter(email=email).exists():
    send_email()

# Use in_bulk for fetching specific objects
users_dict = User.objects.filter(id__in=id_list).in_bulk()
# users_dict is {id: user}

# Check if queryset is empty
if User.objects.filter(status='active').exists():
    process_active_users()
📊 SQL Comparison
sql
-- len(queryset) executes:
SELECT * FROM users;  -- Returns all rows

-- count() executes:
SELECT COUNT(*) FROM users;  -- Returns single number
📌 Rule
Use .count() for counting and .exists() for existence checks

🚀 Advanced Production Optimization Rules
1️⃣ Cache Expensive Queries
python
from django.core.cache import cache
from django.db.models import Count
import hashlib
import json

def get_dashboard_stats():
    # Create cache key based on query parameters
    cache_key = 'dashboard_stats'
    
    # Try to get from cache
    stats = cache.get(cache_key)
    if stats:
        return stats
    
    # Expensive query
    stats = User.objects.annotate(
        post_count=Count('posts'),
        comment_count=Count('comments')
    ).values('id', 'username', 'post_count', 'comment_count')
    
    # Convert to list to evaluate queryset
    stats = list(stats)
    
    # Cache for 1 hour (3600 seconds)
    cache.set(cache_key, stats, 3600)
    
    return stats

# Cache with versioning
def get_user_stats(user_id):
    cache_key = f'user_stats_{user_id}_{user.last_updated}'
    return cache.get_or_set(
        cache_key,
        lambda: calculate_user_stats(user_id),
        300  # 5 minutes
    )

# Template fragment caching
{% load cache %}
{% cache 500 sidebar request.user.id %}
    {% for post in user.posts.all %}
        {{ post.title }}
    {% endfor %}
{% endcache %}
2️⃣ Optimize Queries with select_related and prefetch_related
python
from django.db.models import Prefetch, Q

# Deep prefetching
posts = Post.objects.select_related(
    'author__profile'  # Nested select_related
).prefetch_related(
    'tags',
    Prefetch(
        'comments',
        queryset=Comment.objects.select_related('author')
                       .filter(is_approved=True)
                       .order_by('-created_at')[:10],
        to_attr='recent_comments'
    )
)

# Only prefetch when needed
class PostListView(ListView):
    model = Post
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            # Staff needs more data
            return queryset.prefetch_related(
                'comments__author',
                'tags'
            )
        else:
            # Regular users need less
            return queryset.select_related('author')
3️⃣ Database Connection Pooling
python
# settings.py

# For PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 10 minutes persistent connection
        'OPTIONS': {
            'pool': True,  # Enable connection pooling
            'max_connections': 20,
        }
    }
}

# For MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
        'CONN_MAX_AGE': 600,  # 10 minutes persistent connection
    }
}
4️⃣ Query Optimization with Defer and Only
python
# Get only needed fields
users = User.objects.only('id', 'username', 'email')

# Exclude heavy fields
posts = Post.objects.defer('content', 'html_content')

# Conditional loading
user = User.objects.get(id=1)
if needs_full_profile:
    user = User.objects.get(id=1)  # Reload with all fields
else:
    user = User.objects.only('username').get(id=1)
5️⃣ Use Database Transactions Wisely
python
from django.db import transaction

@transaction.atomic
def process_order(order_id):
    """All operations in single transaction"""
    order = Order.objects.select_for_update().get(id=order_id)
    
    if order.status == 'paid':
        return
    
    # Update inventory
    for item in order.items.all():
        product = Product.objects.select_for_update().get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    # Update order status
    order.status = 'paid'
    order.save()

# Nested transactions
@transaction.atomic
def create_user_with_profile(user_data, profile_data):
    user = User.objects.create(**user_data)
    
    try:
        with transaction.atomic():
            profile = Profile.objects.create(user=user, **profile_data)
    except Exception:
        # Profile creation failed, but user will still be created
        # because it's in outer transaction
        log_error("Profile creation failed")
    
    return user
6️⃣ Raw SQL for Complex Queries
python
from django.db import connection

def get_complex_report(start_date, end_date):
    """When ORM is not enough, use raw SQL"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM orders
            WHERE created_at BETWEEN %s AND %s
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
        """, [start_date, end_date])
        
        rows = cursor.fetchall()
        
        return [
            {
                'month': row[0],
                'unique_users': row[1],
                'total_amount': row[2],
                'avg_amount': row[3]
            }
            for row in rows
        ]

# Raw query with model mapping
for user in User.objects.raw(
    'SELECT id, username FROM auth_user WHERE is_active = %s',
    [True]
):
    print(user.username)
7️⃣ Partitioning Large Tables
python
# models.py - PostgreSQL table partitioning

class Order(models.Model):
    created_at = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        # Define partitioning by date
        indexes = [
            models.Index(fields=['created_at']),
        ]

# In migration, create partitions
"""
-- SQL for PostgreSQL partitioning
CREATE TABLE orders_2024_01 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
"""
8️⃣ Query Optimization with Subqueries
python
from django.db.models import Subquery, OuterRef, Count

# Users with their latest order
latest_orders = Order.objects.filter(
    user=OuterRef('pk')
).order_by('-created_at')

users = User.objects.annotate(
    latest_order_date=Subquery(latest_orders.values('created_at')[:1]),
    latest_order_amount=Subquery(latest_orders.values('amount')[:1])
)

# Posts with comment count from last 24 hours
from django.utils import timezone
from datetime import timedelta

recent_comments = Comment.objects.filter(
    post=OuterRef('pk'),
    created_at__gte=timezone.now() - timedelta(days=1)
).values('post').annotate(
    count=Count('id')
).values('count')

posts = Post.objects.annotate(
    recent_comments=Subquery(recent_comments[:1])
)

# Complex subquery with condition
from django.db.models import Exists

users_with_recent_orders = User.objects.annotate(
    has_recent_order=Exists(
        Order.objects.filter(
            user=OuterRef('pk'),
            created_at__gte=timezone.now() - timedelta(days=30)
        )
    )
)
9️⃣ Use Materialized Views for Complex Reports
python
# management/commands/create_materialized_views.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Create materialized view
            cursor.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS user_statistics AS
                SELECT 
                    u.id as user_id,
                    u.username,
                    COUNT(DISTINCT p.id) as post_count,
                    COUNT(DISTINCT c.id) as comment_count,
                    COALESCE(SUM(o.amount), 0) as total_spent,
                    MAX(o.created_at) as last_order_date
                FROM auth_user u
                LEFT JOIN posts p ON p.author_id = u.id
                LEFT JOIN comments c ON c.user_id = u.id
                LEFT JOIN orders o ON o.user_id = u.id
                GROUP BY u.id, u.username;
                
                CREATE INDEX idx_user_stats_user_id 
                ON user_statistics(user_id);
            """)
            
            # Refresh materialized view
            cursor.execute("REFRESH MATERIALIZED VIEW user_statistics;")
🔟 Query Execution Plan Analysis
python
import time
from django.db import connection, reset_queries

def analyze_query(queryset):
    """Analyze query performance"""
    # Clear previous queries
    reset_queries()
    
    # Time the query
    start = time.time()
    result = list(queryset)
    end = time.time()
    
    # Get query info
    queries = connection.queries
    
    print(f"Query count: {len(queries)}")
    print(f"Total time: {end - start:.4f}s")
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}:")
        print(f"Time: {query['time']}s")
        print(f"SQL: {query['sql']}")
    
    return result

# Use with any queryset
analyze_query(
    Post.objects.select_related('author')
                .prefetch_related('tags')
)

# Get EXPLAIN output
def explain_query(queryset):
    with connection.cursor() as cursor:
        cursor.execute(f"EXPLAIN ANALYZE {queryset.query}")
        return cursor.fetchall()
📊 Query Analysis & Debugging
Django Debug Toolbar Setup
python
# settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

# Custom configuration
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'RESULTS_CACHE_SIZE': 100,
    'SQL_WARNING_THRESHOLD': 100,  # ms
}
Custom Query Logger
python
# utils/query_logger.py
import logging
import time
from django.db import connection

logger = logging.getLogger('django.db.backends')

class QueryLogger:
    def __init__(self):
        self.queries = []
    
    def __call__(self, execute, sql, params, many, context):
        start = time.time()
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            duration = time.time() - start
            self.queries.append({
                'sql': sql,
                'params': params,
                'duration': duration,
                'error': str(e)
            })
            raise
        else:
            duration = time.time() - start
            self.queries.append({
                'sql': sql,
                'params': params,
                'duration': duration,
                'rows': len(result) if hasattr(result, '__len__') else None
            })
            
            # Log slow queries
            if duration > 0.5:  # 500ms threshold
                logger.warning(f"Slow query ({duration:.2f}s): {sql}")
            
            return result

# Usage
with QueryLogger() as logger:
    users = list(User.objects.filter(is_active=True))
    
for query in logger.queries:
    print(f"{query['duration']:.3f}s: {query['sql']}")
Query Count Middleware
python
# middleware/query_count.py
from django.db import connection
import time

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Reset query count
        connection.queries_log.clear()
        
        # Time the request
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        
        # Get query count
        query_count = len(connection.queries)
        
        # Add header with query info
        response['X-Query-Count'] = str(query_count)
        response['X-Query-Time'] = f"{duration:.3f}"
        
        # Log if too many queries
        if query_count > 50:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"High query count ({query_count}) for {request.path}"
            )
        
        return response
⚠️ Common Mistakes That Cause Performance Issues
Mistake	Effect	Solution
Admin dashboard loading all users	High memory usage, slow response	Add pagination, filters
Using .all() for counts	Full table scan, memory issues	Use .count()
Missing select_related	N+1 queries, database overload	Add select_related
No pagination	Process overload, timeout	Implement pagination
Queries in templates	Hidden performance issues	Prepare data in views
Not using indexes	Slow queries on large tables	Add appropriate indexes
Loading entire tables	Memory exhaustion	Use .iterator(), filters
Not using bulk operations	Many small transactions	Use bulk_create, bulk_update
Over-fetching fields	Bandwidth waste, slow serialization	Use .only(), .values()
Not caching	Repeated expensive queries	Implement caching strategy
Using Python for aggregation	Slow processing	Use database aggregation
Not using connection pooling	Connection overhead	Configure CONN_MAX_AGE
Real-world Impact Examples
python
# Example 1: Admin panel loading 10,000 users
# BAD
```
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'post_count']
    
    def post_count(self, obj):
        return obj.posts.count()  # N+1 query!
```
# GOOD
```
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'post_count']
    list_select_related = ['profile']  # Prefetch relations
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            post_count=Count('posts')  # Aggregate in DB
        )
```
# Example 2: API endpoint returning 1000 posts
# BAD - 1001 queries
```
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```
# GOOD - 2 queries
```
class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related(
        'tags', 'comments'
    )
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination  # Add pagination
```
# Example 3: Background job processing 50,000 records
# BAD - Memory intensive
```
def process_all_users():
    for user in User.objects.all():  # Loads all users
        process_user(user)
```
# GOOD - Memory efficient
```
def process_all_users():
    for user in User.objects.filter(is_active=True).iterator(chunk_size=1000):
        process_user(user)
```
🎯 Golden Rules for Production Django
✅ DO's
Use pagination everywhere - Never return unbounded querysets

Always use select_related / prefetch_related - Prevent N+1 queries

Filter querysets - Never trust .all() in production

Index frequently filtered fields - Especially in WHERE, JOIN, ORDER BY

Aggregate in database - Let the DB do what it's good at

Cache heavy queries - Use Django's cache framework

Monitor query count - Set up alerts for high query counts

Optimize admin separately - Admin panels need extra optimization

Use connection pooling - Reduce connection overhead

Profile before optimizing - Use tools to find real bottlenecks

❌ DON'Ts
Don't query in loops - Always batch fetch related data

Don't use len(queryset) - Use .count() instead

Don't load entire tables - Use filters and pagination

Don't ignore database indexes - They're crucial for performance

Don't process in Python what DB can do - Use aggregation

Don't forget about memory - Use iterator() for large datasets

Don't over-fetch fields - Request only what you need

Don't ignore the query count - Set reasonable limits

Don't use default pagination - Customize for your needs

Don't skip testing - Include performance tests

📈 Performance Testing & Monitoring
Performance Checklist
python
# Before deploying to production, verify:

def performance_checklist():
    checks = [
        "All views have pagination",
        "All ForeignKey lookups use select_related",
        "All ManyToMany lookups use prefetch_related",
        "No .all() without filters in views",
        "Database indexes on all filtered fields",
        "Bulk operations for batch inserts/updates",
        "Query count < 50 per page",
        "Response time < 500ms for 95th percentile",
        "Memory usage < 256MB per request",
        "Caching for expensive operations",
        "Connection pooling configured",
        "No N+1 queries in templates",
        "Database migrations optimized",
        "Slow query logging enabled",
        "Database connection limits set"
    ]
    
    return checks
Quick Reference Card
python
# Quick reference for common scenarios

# 1. Get user with profile and recent orders
user = User.objects.select_related('profile').prefetch_related(
    Prefetch('orders', queryset=Order.objects.order_by('-created_at')[:5])
).get(id=user_id)

# 2. Get active posts with authors and top comments
posts = Post.objects.filter(is_published=True).select_related('author').prefetch_related(
    Prefetch('comments', 
             queryset=Comment.objects.filter(is_approved=True)
                            .select_related('author')[:3],
             to_attr='top_comments')
)

# 3. Bulk create with related objects
posts = []
for i in range(100):
    posts.append(Post(title=f'Post {i}', author=author))
Post.objects.bulk_create(posts)

# 4. Efficient counting and existence
if User.objects.filter(email=email).exists():
    # Do something
    pass

# 5. Aggregation example
stats = Order.objects.filter(status='paid').aggregate(
    total=Sum('amount'),
    count=Count('id'),
    avg=Avg('amount')
)

# 6. Pagination
from django.core.paginator import Paginator

paginator = Paginator(Post.objects.select_related('author'), 20)
page = paginator.get_page(request.GET.get('page'))

# 7. Caching
from django.core.cache import cache

def get_expensive_data():
    data = cache.get('expensive_key')
    if not data:
        data = expensive_query()
        cache.set('expensive_key', data, 3600)
    return data

# 8. Only specific fields
users = User.objects.only('id', 'username', 'email').filter(is_active=True)

# 9. Iterator for large datasets
for user in User.objects.all().iterator(chunk_size=1000):
    process_user(user)

# 10. Raw SQL when needed
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    row = cursor.fetchone()
⚙️ Installation & Setup
Prerequisites
bash
# Ensure you have the following installed
Python 3.8+
Django 3.2+
Database (PostgreSQL/MySQL/SQLite)
Redis/Memcached (optional, for caching)
Quick Start
bash
# Clone the repository
git clone https://github.com/Nishanchaudhary/django-query-optimization-guide.git

# Navigate into the project directory
```
cd django-query-optimization-guide

# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows
env\Scripts\activate
# Mac/Linux
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database in settings.py
# Run migrations
python manage.py migrate

# Run development server
python manage.py runserver
Configuration Example
python
```
# settings.py

# Database configuration with connection pooling
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 10 minutes persistent connection
        'OPTIONS': {
            'pool': True,
        }
    }
}
```
# Caching configuration
```
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

# Logging configuration for slow queries
```
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```
##📝 Contributing
Contributions are welcome! Here's how you can help:

Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

Contribution Guidelines
Add clear examples for new optimization techniques

Include performance comparisons where applicable

Update documentation with your changes

Follow PEP 8 style guide

Write descriptive commit messages

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Contact
Nishan Kumar Chaudhary

Email: chaudharynishan314@gmail.com

GitHub: @Nishanchaudhary

LinkedIn: Nishan Chaudhary

Live Demo: bginfotechs.com.np

Support
⭐ Star this repository if you find it helpful

🐛 Report issues on GitHub Issues

💡 Suggest new features via pull requests

🙏 Acknowledgments
Django Documentation Team

Django Debug Toolbar Contributors

PostgreSQL Performance Community

All contributors and reviewers

Remember: The key to Django performance is understanding what happens at the database level. Always profile before optimizing, and measure the impact of your changes. Happy optimizing! 🚀

<div align="center"> Made with ❤️ by Nishan Kumar Chaudhary </div>
