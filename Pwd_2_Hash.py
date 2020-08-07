#Terminal based program where which is used in the main file...
#Firstly the program is converted to ciphrt text anf using the inbuilt hash punction converting that to a hash value ...

pwd = input("Enter the password : ")

Spl_chr_Even = "N#a&RaK9" 
Spl_chr_Odd = "!Kar)*(an"

new_pwd=[]

def ENCRYPT(plain):
    global key,key_len
    plain_split = []
    cipher=[]
    plain = list(plain)

    for i in range(0,len(plain),key_len):
        temp = []
        for j in range(key_len):
            temp.append(plain[i+j])
        plain_split.append(''.join(temp))
    
    for i in range(len(plain_split)):
        if i == 0:
            cipher.append(GET_CIPHER(plain_split[i],key))
        else:
            cipher.append(GET_CIPHER(plain_split[i],cipher[i-1]))

    return("".join(cipher))

def GET_CIPHER(plain,key):
    ans=[]
    for i in range(len(plain)):
        x = ord(plain[i])
        y = ord(key[i])
        if i%2 == 0:
            for j in range(y):
                x+=1
                if x==127:
                    x=32
        else:
            for j in range(y):
                x-=1
                if x==31:
                    x=126
        ans.append(chr(x))
    return("".join(ans))

if len(pwd)%2 == 0:
    new_pwd.append(Spl_chr_Odd)
    for i in range(len(pwd)//2):
        new_pwd.append(pwd[i])
    new_pwd.append(Spl_chr_Even)
    for i in range(len(pwd)//2,len(pwd)):
        new_pwd.append(pwd[i])
    new_pwd.append(Spl_chr_Odd[::-1])
else:
    new_pwd.append(Spl_chr_Even[::-1])
    for i in range(len(pwd)//2):
        new_pwd.append(pwd[i])
    new_pwd.append(Spl_chr_Odd)
    for i in range(len(pwd)//2,len(pwd)):
        new_pwd.append(pwd[i])
    new_pwd.append(Spl_chr_Even)

new_pwd = "".join(new_pwd)

text = new_pwd[:len(new_pwd)//2]
key = new_pwd[len(new_pwd)//2:]

key_len = len(key)

x = ENCRYPT(text)
print(x)
hash_val = hash(x)

print(hash_val)