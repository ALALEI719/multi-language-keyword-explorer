import bcrypt

# 这里是我们想要设置的密码
password = 'abc12345'

# 生成哈希值（使用bcrypt）
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print("--------------------------------------------------")
print(f"原始密码: {password}")
print(f"生成的Hash (请复制下面这一行):")
print(hashed_password)
print("--------------------------------------------------")