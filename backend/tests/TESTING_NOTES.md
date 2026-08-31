# Testing notes

# Core testing principles
**Test the contract of the function**

- Only validate the behavior this function is responsible for.

- Do not retest downstream logic unnecessarily.

**Fake objects simulate behavior, not real infrastructure**

- FakeDB does not execute real SQL.
- It only returns controlled outputs for deterministic tests.

**Happy path vs failure path**

- Happy path tests successful behavior
- Failure path tests invalid/rejected behavior

**Unit tests isolate logic**

Unless writing integration tests, avoid real:

- databases
- HTTP requests
- external systems


## test_security.py

* [Jump to test_get_session_returns_session_for_valid_session_id()] (#test_get_session_returns_session_for_valid_session_id)


### test_get_session_returns_session_for_valid_session_id
<br>
<br>

**The actual code**
```python
def test_get_session_returns_session_for_valid_session_id():
    fake_session = (123, "expires")

    result = get_session("abc123", FakeDB(fake_session))

    assert result == fake_session
```


The point of this test is 

* NO datetime comparison
* NO expiration validation
* NO timezone logic

Only:
* queries DB
* returns raw data

Basically we only care about did the function return the DB result correctly?

```
fake_session = (123, "expires")
```

123 is filling in for user_id and expires is filling in for expires_at. Since we are not doing any logic here and only care that does get_session() return whatever fetchone() returns, "expires" is fine. 

```
assert result == fake_session
```
This is basically verifying

**function output == fake DB output**

We do not care about:
* business logic
* auth logic
* expiration logic

High level explanation

Step 1. get_session() calls the below function and stores it in session

```python
def get_session(session_id: str, db):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, expires_at
            FROM sessions
            WHERE session_id = ? AND revoked = FALSE
        """, (session_id,))
        return cursor.fetchone()
```

Step 2. The function replaces params 
```python
get_session("abc123", FakeDB(fake_session))
```
So in effect
* session_id becomes "abc123"
* db becomes FakeDB(fake_session)

Step 3. The fake DB is used

Inside the real function we would use:
```python
with db.cursor() as cursor:
```
but instead the fake db returns
```python
FakeCursor(fake_session)
```

Step 4. execute() runs

```python
cursor.execute(SQL, ("abc123",))
```
So now the fake cursor is storing
```python
self.query = SQL
self.params = ("abc123",)
```
Important note: The fake cursor stores query information but does not execute real SQL.

Step 5. fetchone() runs

In the real function this runs
```python
return cursor.fetchone()
```
which calls
```python
FakeCursor.fetchone()
```
the above then returns
```python
self.result
```
which is
```python
fake_session
```

**Important note**

"Abc123" doesn't matter here for any logic purposes. Remember, we only care about does get_session() return fetchone() correctly. The ***only*** reason we care about it is because session_id is required here is because the real function needs it for a parameter. In effect the fake db is simulating “Pretend the DB already found this session.”

* "abc123" is just the lookup key
* fake_session is the simulated DB result

TL:DR The fake DB bypasses real SQL execution and directly returns the configured fake_session result through fetchone().

<br>
<br>

### test_get_valid_session_raises_when_session_id_missing
<br>
<br>

**The actual code**
```python
def test_get_valid_session_raises_when_session_id_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_valid_session(None, FakeDB(None))

    assert exc_info.value.status_code == 401
```

We EXPECT this code to throw an HTTPException. If no exception is encountered, this will fail.

```python
as exc_info
```
is basically 
```python
caught_exception = ...
```

```python
get_valid_session(None, FakeDB(None))
```

We simulate: no session_id cookie and fake DB is unused here. This triggers:

```python
if not session_id:
```

Here we inspect captured exception and verify correct status code
```python
assert exc_info.value.status_code == 401
```

<br>
<br>

### test_get_valid_session_raises_when_session_expired

<br>
<br>

Most of the below function is self explanatory:

```python
def test_get_valid_session_raises_when_session_expired():
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)

    fake_session = (123, expired_time)

    with pytest.raises(HTTPException) as exc_info:
        get_valid_session("abc123", FakeDB(fake_session))

    assert exc_info.value.status_code == 401
```

Except this part:

```python
expired_time = datetime.now(timezone.utc) - timedelta(days=1)
```
This means:
- "one day in the past."

Basically:
- expired session


<br>
<br>

### test_get_valid_session_returns_session_when_valid

<br>
<br>

Most of the below function is self explanatory:

```python
def test_get_valid_session_returns_session_when_valid():
    future_time = datetime.now(timezone.utc) + timedelta(days=1)

    fake_session = (123, future_time)

    result = get_valid_session("abc123", FakeDB(fake_session))

    assert result == fake_session
```

What this validates:

- successful authentication path
- happy-path auth test

We simulate:

- valid session_id
- valid DB session
- future expiration

Expected:

session returned successfully


### test_get_valid_session_handles_naive_datetime

<br>
<br>

The below deceptively simple test is actually quite complicated:

```python
def test_get_valid_session_handles_naive_datetime():
    naive_future_time = datetime.now() + timedelta(days=1)

    fake_session = (123, naive_future_time)

    result = get_valid_session("abc123", FakeDB(fake_session))

    assert result == fake_session
```

What this validates: **Can the auth system safely handle naive datetimes?**

Step 1. Create the naive datetime

```python
naive_future_time = datetime.now() + timedelta(days=1)
```

Important to note that:

datetime.now() does **NOT** equal datetime.now(timezone.utc)

datetime.now() returns a datetime **WITHOUT** timezone information.

For example (a naive time zone)

```
2026-05-18 22:15:00
#tzinfo = None
```

The below basically means “one day into the future” so our session should still be valid.
```python
+ timedelta(days=1)
```

Step 2. Create a fake db session

This is simulating (user_id, expires_at) being returned from the db.
```python
fake_session = (123, naive_future_time)
```

Step 3. Call the function during testing

This triggers the real auth validation logic
```python
result = get_valid_session("abc123", FakeDB(fake_session))
```
#### What is happening inside the function

The real code is validating session_id exists:

```python
if not session_id:
```

This passes because "abc123" exists.

We query our fake db
```python
session = get_session(session_id, db)
```

Then our fake db returns

```python
(123, naive_future_time)
```

After we unpack our session

```python
user_id, expires_at = session
```

That now turns into:

```python
user_id = 123
expires_at = naive_future_time
```

Now the below line runs because we intentionally created a naive datetime:
```python
if expires_at.tzinfo is None:
```

This is now true
```python
expires_at.tzinfo == None
```

Now we normalize the timezones so this runs:

```python
expires_at = expires_at.replace(tzinfo=timezone.utc)
```
naive datetime -> UTC-aware datetime

If we didn't normalize Python would choke on the below line:

```python
if expires_at < datetime.now(timezone.utc):
```

Step 5. Compare expiration
Now the normalized datetime is compared against current UTC time. Now the session is still valid so no exception is raised.

```python
future_time > now
```

Step 5. Return session
The function returns

```python
return session
```

Which in reality is (123, naive_future_time) and stored into "result"

Our final assertion verifies:

- function completed successfully
- timezone normalization prevented failure
- session validation still passed

```python
assert result == fake_session
```