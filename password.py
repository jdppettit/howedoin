import md5


def hashPassword(password):
    m = md5.new()
    m.update(password)
    m.update(
        "TGFQJH#()*tfgHQA@EghAEUJgvb A#W)EQA#RT#QUTGHE@Q*RFHQRQFDsifjaij@D*()q238r9q3e4#)*@(%$&!^@)#*!@&#")
    return m.hexdigest()
