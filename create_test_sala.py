import psycopg2
from jose import jwt

# Conectar a la base de datos
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='root', database='parcialsw')
cur = conn.cursor()

# Generar tokenS
tokenS = jwt.encode({'newSalas': {'title': 'Sala de Prueba', 'user_id': 1}}, 'token_sala', algorithm='HS256')

# Insertar sala
cur.execute('INSERT INTO salas (title, description, xml, "tokenS", user_id) VALUES (%s, %s, %s, %s, %s)', 
            ('Sala de Prueba', 'Descripción de prueba', '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>', tokenS, 1))

conn.commit()
print(f'Sala creada con tokenS: {tokenS}')

cur.close()
conn.close()
