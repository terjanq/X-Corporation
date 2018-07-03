import psycopg2
import argparse
import sys
import json
from hashlib import md5

# common functions

def parseArgs():
    parser = argparse.ArgumentParser(description='X Corp Managing')
    parser.add_argument('--init', help='initial run', action='store_true')

    return parser, parser.parse_args()

def initTables(cur, conn):
    queries = open("tables.sql", "r").read();
    cur.execute(queries)
    conn.commit()


def connectToDB(**login_data):
    conn = psycopg2.connect(**login_data)
    cur = conn.cursor()
    return cur, conn


def printError(**args):
    res = { "status": "ERROR" }
    if 'msg' in args:
        res["debug"] = args['msg']
    sys.stdout.write(json.dumps(res) + '\n')
    if 'exit' in args:
        exit(-1)

def printOK(**args):
    res = { "status": "OK" }
    if 'data' in args:
        res['data'] = args['data']
    if 'msg' in args:
        res['debug'] = args['msg']

    sys.stdout.write(json.dumps(res) + '\n')


# db queries

def auth(e_id, pwd, cur):
    cur.execute('''SELECT emp_password FROM "Employee_auth" WHERE emp_id = %s''', [e_id])
    pswd = cur.fetchone()
    pswd = pswd[0] if pswd else None
    return pswd == md5(pwd.encode('utf-8')).hexdigest()

def insertUser(cur, e_id, e_sup, pwd, data):
    if userExists(e_id, cur):
        return False
    i_data = (e_id, e_sup, md5(pwd.encode('utf-8')).hexdigest(), data)
    cur.execute( ''' SELECT insert_employee(%s, %s, %s, %s) ''', i_data )
    return cur.fetchone() != None

def update(e_id, id, inf_end, cur):
    cur.execute('''SELECT update_po(%s, %s, %s)''', [e_id, id, inf_end])

def userExists(emp, cur):
    cur.execute(''' SELECT 1 FROM "Employee_relations" WHERE emp_id = %s LIMIT 1 ''', [emp])
    return cur.fetchone() != None

def ancestor(emp2, emp1, cur):
    query = '''
    WITH inf AS (
        SELECT id
        FROM "Employee_relations"
        WHERE emp_id = %s
        LIMIT 1
    )
    SELECT 1 FROM "Employee_relations"
    WHERE emp_id = %s AND (SELECT id FROM inf) BETWEEN id + 1 and inferior_end LIMIT 1
    '''

    cur.execute(query, [emp1, emp2])
    one = cur.fetchone()
    return one != None

def readdata(cur, emp):
    query = '''
        SELECT emp_data FROM "Employee_data"
        WHERE emp_id = %s
    '''
    cur.execute(query, [emp])
    return cur.fetchone()

def descendants(cur, emp):
    query = '''
        WITH sup AS (
            SELECT id, inferior_end
            FROM "Employee_relations"
            WHERE emp_id = %s
        )
        SELECT emp_id FROM "Employee_relations" WHERE id BETWEEN (SELECT id FROM sup) + 1 and (SELECT inferior_end FROM sup) ORDER BY id
    '''
    cur.execute(query, [emp])
    return list(map(lambda x: x[0], cur.fetchall()))

def childs(cur, emp):
    query = '''
        SELECT emp_id FROM "Employee_relations"
        WHERE emp_superior = %s ORDER BY emp_superior
    '''
    cur.execute(query, [emp])
    return list(map(lambda x: x[0], cur.fetchall()))

def ancestors(cur, emp):
    query = '''
        WITH inf AS (
            SELECT id
            FROM "Employee_relations"
            WHERE emp_id = %s
        )
        SELECT emp_id FROM "Employee_relations" WHERE (SELECT id FROM inf) BETWEEN id + 1 and inferior_end ORDER BY id
    '''
    cur.execute(query, [emp])
    return list(map(lambda x: x[0], cur.fetchall()))


def removeEmp(cur, emp):
    query = '''
        SELECT remove_employee(%s)
    '''
    cur.execute(query, [emp])
    return cur.fetchone() != None

def insertRoot(cur, root):
    query = ''' INSERT INTO "Employee_root" VALUES(%s) '''
    cur.execute(query, [root])

def getRoot(cur):
    query = ''' SELECT emp_id FROM "Employee_root" '''
    cur.execute(query)
    return cur.fetchone()[0]

def parent(cur, emp):
    query = '''
        SELECT emp_superior FROM "Employee_relations"
        WHERE emp_id = %s
    '''
    cur.execute(query, [emp])
    res = cur.fetchone()


# handle events

def checkBasic(cur, emp, admin, passwd):
    if not auth(admin, passwd, cur):
        printError(msg="Authentication error for `%s`" % admin)
        return False
    if not userExists(emp, cur):
        printError(msg="User `%s` does not exist" % emp)
        return False
    return True

def handleNewInit(cur, root, emp, emp1, newpasswd, data, admin, passwd):
    if admin != root or auth(admin, passwd, cur) == False:
        printError(msg="Authentication fail for `%s`" % admin)
        return;
    if not userExists(emp1, cur):
        printError(msg="User `%s` does not exist" % emp1)
        return
    if insertUser(cur, emp, emp1, newpasswd, data):
        printOK()
    else:
        printError(msg="insert error")

def handleNew(cur, emp, emp1, newpasswd, data, admin, passwd):
    if not checkBasic(cur, emp1, admin, passwd):
        return
    if emp1 != admin and ancestor(admin, emp1, cur) == False:
        printError(msg="Admin `%s` is not ancestor of `%s`" % (admin, emp1))
        return
    if insertUser(cur, emp, emp1, newpasswd, data):
        printOK()
        postOrder(cur, getRoot(cur), 0, [0])
    else:
        printError(msg="create error")

def handleAncestor(cur, emp1, emp2, admin, passwd):
    if not auth(admin, passwd, cur):
        printError(msg="Authentication error")
        return
    if not userExists(emp1, cur) or not userExists(emp2, cur) :
        printError(msg="User `%s` does not exist" % emp)
        return
    if ancestor(emp2, emp1, cur):
        printOK(data=["true"])
    else:
        printOK(data=["false"])

def handleParent(cur, emp, admin, passwd):
    if not checkBasic(cur, emp, admin, passwd):
        return
    res = parent(cur, emp)
    printOK(data=[res])

def handleUpdate(cur, admin, passwd, emp, newdata):
    if not checkBasic(cur, emp, admin, passwd):
        return
    if emp != admin and not ancestor(admin, emp, cur):
        printError(msg="Admin `%s` is not ancestor of `%s`" % (admin, emp))
        return
    query = '''
        UPDATE "Employee_data" SET emp_data = %s
        WHERE emp_id = %s
    '''
    cur.execute(query, [newdata, emp])
    printOK()

def handleRead(cur, admin, passwd, emp):
    if not checkBasic(cur, emp, admin, passwd):
        return
    if emp != admin and not ancestor(admin, emp, cur):
        printError(msg="Admin `%s` is not ancestor of `%s`" % (admin, emp))
        return
    res = readdata(cur, emp)
    printOK(data=[res[0]])

def handleChild(cur, admin, passwd, emp):
    if not checkBasic(cur, emp, admin, passwd):
        return
    res = childs(cur, emp)
    printOK(data=res)

def handleAncestors(cur, admin, passwd, emp):
    if not checkBasic(cur, emp, admin, passwd):
        return
    res = ancestors(cur, emp)
    printOK(data=res)



def handleRemove(cur, admin, passwd, emp):
    if not checkBasic(cur, emp, admin, passwd):
        return
    if not ancestor(admin, emp, cur):
        printError(msg="Admin `%s` is not ancestor of `%s`" % (admin, emp))
        return
    e_descendants = [emp]
    e_descendants += descendants(cur, emp)

    for e in e_descendants:
        if not removeEmp(cur, e):
            printError(msg='delete error')
            return
    printOK()

def handleDescendants(cur, admin, passwd, emp):
    if not checkBasic(cur, emp, admin, passwd):
        return
    res = descendants(cur, emp)
    printOK(data = res)
    return

def handleOpen(mode, login, password, database):
    db_init = {
        "user": mode,
        "password": "qwerty",
        "host": "127.0.0.1",
        "port": "5432",
        "database": database
    }

    if login != mode:
        printError(msg="Wrong username", exit=1)

    if password != 'qwerty':
        printError(msg='Wrong password', exit=1)

    return connectToDB(**db_init)


def handleRoot(cur, secret, newpassword, data, emp):
    if secret != 'qwerty':
        printError(msg="Wrong secret code", exit=1)

    r_data = ( emp, None, newpassword, data )
    insertUser(cur, *r_data)
    insertRoot(cur, emp)


# Post-order functions:

def postOrder(cur, root, current, counter):

    query = '''
        SELECT emp_id FROM "Employee_relations"
        WHERE emp_superior = %s
    '''
    cur.execute(query, [root])

    for child in cur.fetchall():
        counter[0] += 1;
        postOrder(cur, child, counter[0], counter)

    update(root, current, counter[0], cur)


# main functions

def handleFunction(name, body, cur, con):
    if name == 'ancestor':
        handleAncestor(cur, **body)
    elif name == 'parent':
        handleParent(cur, **body)
    elif name == 'update':
        handleUpdate(cur, **body)
    elif name == 'read':
        handleRead(cur, **body)
    elif name == 'new':
        handleNew(cur, **body)
    elif name == 'child':
        handleChild(cur, **body)
    elif name == 'ancestors':
        handleAncestors(cur, **body)
    elif name == 'descendants':
        handleDescendants(cur, **body)
    elif name == 'remove':
        handleRemove(cur, **body)
    else:
        printError(msg="unknown function")


def handleInit():
    u_init = {
        "user": "init",
        "password": "qwerty",
        "host": "127.0.0.1",
        "port": "5432",
        "database": "XCorp"
    }

    # add error handling
    i_open = json.loads(sys.stdin.readline())['open']
    cur, con = handleOpen('init', **i_open)
    printOK(msg="connected")

    initTables(cur, con)

    i_root = json.loads(sys.stdin.readline())['root']
    handleRoot(cur, **i_root)

    for line in sys.stdin:
        i_new = json.loads(line)['new']
        handleNewInit(cur, i_root['emp'], **i_new)

    con.commit()
 
    postOrder(cur, i_root['emp'], 0, [0])
    con.commit()

def handleInput():

    i_open = json.loads(sys.stdin.readline())['open']
    cur, con = handleOpen('app', **i_open)
    printOK(msg="connected")
    
    for line in sys.stdin:
        l_func = json.loads(line)
        l_func_name = next(iter(l_func))
        l_func_body = l_func[l_func_name]
        handleFunction(l_func_name, l_func_body, cur, con)

    con.commit()

def main():
    parser, args = parseArgs()

    if args.init:
        handleInit()
    else:
        handleInput()

main()


