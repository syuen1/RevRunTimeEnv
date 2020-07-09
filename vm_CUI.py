import re
import sys
import os
import time
from multiprocessing import Process, Value, Array, Lock
codes=[]
com=[]
opr=[]
stack=[]
rstack=[]
temp=[]
ldata=[]
rdata=[]
top=-1
count_pc=0
parflag=0
args=sys.argv

#push:
def push(a,stack,top):
    stack.append(a)
    return top+1

#pop1:
def pop1(stack,top):
    t=stack[top-1]
    stack.pop()
    return (t,top-1)

def executedcommand(stack,rstack,lstack,com,opr,pc,pre,top,rtop,ltop,address,value,parpath,tablecount,variable_region):
    if com==1:#push
        top=push(opr,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==2:#load
        value.acquire()
        c=value[opr]
        value.release()
        top=push(c,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==3:#store
        value.acquire()
        rstack[rtop.value]=(value[opr])
        rstack[rtop.value+1]=(parpath)
        rtop.value=rtop.value+2
        (stack[opr],top)=pop1(stack,top)
        value[opr]=stack[opr]
        value.release()
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==4:#jpc
        (c,top)=pop1(stack,top)
        if c==1:
            pre=pc
            pc=opr-2
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==5:#jmp
        pre=pc
        pc=opr-2
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==6:#op
        if (opr)==0:#'+'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c+d,stack,top)
        elif (opr)==1:#'*'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c*d,stack,top)
        elif opr==2:#'-'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(d-c,stack,top)
        elif opr==3:#'>'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            if d>c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        elif opr==4:#'=='
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            if d==c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==7:#label
        if args[2]=='f':
            lstack[ltop.value]=(pre)
            lstack[ltop.value+1]=parpath
            ltop.value = ltop.value+2
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==8:#rjmp
        pre=pc
        ltop.value=ltop.value-1
        pc=int(lstack[ltop.value])
        pc=pc-2
        ltop.value=ltop.value-1
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==9:#restore
        rtop.value=rtop.value-1
        value[opr]=int(rstack[rtop.value])
        rtop.value=rtop.value-1
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==0:#nop
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==10:#par
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==11:#alloc
        top=push(int(variable_region[opr]),stack,top)
        value[opr] = int(variable_region[opr])
        tablecount.value=tablecount.value+1
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount)
    elif com==12:#free
        (a,top)=pop1(stack,top)
        tablecount.value=tablecount.value-1
        pre=pc
        variable_region[opr] = value[opr]
        return (pc+1,pre,stack,top,rtop,tablecount)

def execution(mode,lock,mlock,command,opr,start,end,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag,parpath,variable_region):
    pc=start
    pre=pc
    top=len(stack)
    num_variables = tablecount.value
    if args[2]=='f':
        while pc<end:
            if parpath!=0:
               lock.acquire()
            if args[3]!='q':
                if command[pc]==1:
                    command1='ipush'
                elif command[pc]==2:
                    command1=' load'
                elif command[pc]==3:
                    command1='store'
                elif command[pc]==4:
                    command1='  jpc'
                elif command[pc]==5:
                    command1='  jmp'
                elif command[pc]==6:
                    command1='   op'
                elif command[pc]==7:
                    command1='label'
                elif command[pc]==10:
                    command1='  par'
                elif command[pc]==11:
                    command1='alloc'
                elif command[pc]==12:
                    command1=' free'
                print("~~~~~~~~Process"+str(parpath)+" execute~~~~~~~~")
                print("pc = "+str(pc+1)+"   command = "+command1+"   operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop,tablecount)=executedcommand(stack,rstack,lstack,command[pc],opr[pc],pc,pre,top,rtop,ltop,address,value,parpath,tablecount,variable_region)
            if args[3]!='q':
                print("executing stack:       "+str(stack[3:])+"")
                print("shared variable stack: "+str(value[0:tablecount.value])+"")
            if command[pre] == 12:
                with open("variable_region.txt",'w') as f:
                    for i in range(0,num_variables,1):
                        f.write(""+str(variable_region[i])+" ")
            if parpath!=0:
                if mode=='2':
                    lock.acquire(False)
                    mlock.release()
                elif mode=='1':
                    lock.release()
        endflag.value=1
    #backward mode
    elif args[2]=='b':
        while pc<end:
            if parpath!=0:
                lock.acquire()
            if args[3]!='q':
                if command[pc]==0:
                    command1='    nop'
                elif command[pc]==7:
                    command1='  label'
                elif command[pc]==8:
                    command1='   rjmp'
                elif command[pc]==9:
                    command1='restore'
                elif command[pc]==10:
                    command1='    par'
                elif command[pc]==11:
                    command1='  alloc'
                elif command[pc]==12:
                    command1='   free'
                print("~~~~~~~~Process"+str(parpath)+" execute~~~~~~~~")
                print("pc = "+str(pc+1)+"   command = "+command1+"   operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop,tablecount)=executedcommand(stack,rstack,lstack,command[pc],opr[pc],pc,pre,top,rtop,ltop,address,value,parpath,tablecount,variable_region)
            if args[3]!='q':
                print("shared variable stack: "+str(value[0:tablecount.value])+"")
            if parpath!=0:
                lock.acquire(False)
                mlock.release()
        endflag.value=1
        with open("variable_region.txt",'w') as f:
            for i in range(0,len(variable_region),1):
                f.write(""+str(variable_region[i])+" ")
    return stack        

def coderead(start,end,variable_region):
    global codes
    global com
    global opr
    global count_pc
    global parflag
    f=open(args[1],mode='r')
    codes=f.read()
    f.close()
    for i in range(0,len(codes),9):
        t1=codes[i:i+2]
        s1=re.search(r'\d+',t1)
        t2=codes[i+2:i+8]
        s2=re.search(r'\d+',t2)
        com.append((int)(s1.group()))
        opr.append((int)(s2.group()))
        if ((int)(s1.group())==10 and (int)(s2.group())==0):
            start.append(count_pc)
        elif ((int)(s1.group())==10 and (int)(s2.group())==1):
            end.append(count_pc)
            parflag=parflag+1
        count_pc=count_pc+1
        with open("variable_region.txt","r") as f:
            buf = f.read()
            variable_region = re.findall(r'[-]?\d+',buf)
    return (start,end,variable_region)

def backward():
    global ldata
    global rdata
    global stack
    if args[2]=='b':
        path4='lstack.txt'
        path5='rstack.txt'
        path7='stack.txt'
        f4=open(path4,mode='r')
        f5=open(path5,mode='r')
        f7=open(path7,mode='r')
        temp=f4.read()
        ldata=re.findall(r'[-]?\d+',temp)
        temp=f5.read()
        rdata=re.findall(r'[-]?\d+',temp)
        temp=f7.read()
        stack=re.findall(r'[-]?\d+',temp)
        f4.close()
        f5.close()
        f7.close()

def forward(ltop,rtop):
    if args[2]!='f' and args[2]!='b':
        path2=args[2]
        f2=open(path2,mode='w')
        for i in range(0,count_pc,1):
            if com[count_pc-i-1]==7:
                f2.write(" 8     0\n")
            elif com[count_pc-i-1]==3:
                f2.write(" 9 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            elif com[count_pc-i-1]==4:
                f2.write(" 7     0\n")
            elif com[count_pc-i-1]==5:
                f2.write(" 7     0\n")
            elif com[count_pc-i-1]==10:
                f2.write("10 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            elif com[count_pc-i-1]==11:
                f2.write("12 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            elif com[count_pc-i-1]==12:
                f2.write("11 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            else:
                f2.write(" 0     0\n")
        f2.close()
        #print("forward code is converted into inverting code.")
    elif args[2]=='f':
        path='lstack.txt'
        f=open(path,'w')
        for i in range(0,ltop,2):
            f.write(""+str(count_pc-lstack[i])+" "+str(lstack[i+1])+" ")
        f.close()

        path3='rstack.txt'
        f3=open(path3,'w')
        for i in range(0,rtop,1):
            f3.write(""+str(rstack[i])+" ")
        f3.close()

        path6='stack.txt'
        f6=open(path6,'w')
        for i in range(0,len(value),1):
            f6.write(""+str(value[i])+" ")
        f6.close()

if __name__ == '__main__':
    start_time = time.time()
    start=[]
    end=[]
    tabledata=[]
    tablecount= Value('i',0)
    address = Array('i',10)
    value = Array('i',10)
    rstack = Array('i',100000)
    lstack = Array('i',100000)
    rtop = Value('i',0)
    ltop = Value('i',0)
    endflag={}
    endflag0=Value('i',0)
    notlabelflag=0
    lock={}
    variable_region = []
    
    mlock = Lock()
    lockfree  = Lock()
    a='1'
    if os.path.getsize("variable_region.txt") <=0:
        with open("variable_region.txt",'w') as f:
            f.write("0 0 0")
    path='table.txt'
    f=open(path,mode='r')
    tabledata=f.read()
    f.close()
    k=0

    backward()

    if len(sys.argv)<4:
        #print("convert into inv_code.txt")
        coderead(start,end,variable_region)
        forward(ltop.value,rtop.value)
        sys.exit()
    #forward mode
    if args[2]=='f':
        (start,end,variable_region)=coderead(start,end,variable_region)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            lock[i] = Lock()
        if parflag!=0:
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto 2:select >> ')
            stack=execution(mode,lockfree,lockfree,com,opr,0,start[0],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
            if mode=='2':
                for i in range(0,parflag,1):
                    lock[i].acquire()
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[i],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1,variable_region))
            if mode=='1':
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[0],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1,variable_region))
            for i in range(0,parflag,1):
                    process[i].start()
            if mode=='2':
                while a!='esc':
                    a=input('>> ')
                    mlock.acquire(False)
                    ifflag=0
                    for i in range(0,parflag,1):
                        if a==str(i+1) and endflag[i].value!=1 and ifflag==0:
                            ifflag=1
                            lock[i].release()
            for i in range(0,parflag,1):
                process[i].join()
            for i in range(0,tablecount.value,1):
                stack[i]=value[i]
            execution(mode,lockfree,lockfree,com,opr,end[parflag-1]+1,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        elif parflag==0:
            mode='1'
            execution(mode,lockfree,mlock,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        forward(ltop.value,rtop.value)

    elif args[2]=='b':
        (start,end,variable_region)=coderead(start,end,variable_region)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            lock[i] = Lock()
        for i in range(0,len(ldata),1):
            lstack[i]=int(ldata[i])
            ltop.value=ltop.value+1
        for i in range(0,len(rdata),1):
            rstack[i]=int(rdata[i])
            rtop.value=rtop.value+1
        #for i in range(0,len(stack),1):
            #value[i]=int(stack[i])
        ltop.value=ltop.value-1
        rtop.value=rtop.value-1
        mode='0'
        if parflag!=0:
            #______measure time mode_________ 
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto  2:select >> ')
            for i in range(0,parflag,1):
                lock[i].acquire()
            process={}
            execution(mode,lockfree,lockfree,com,opr,0,end[0],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
            for i in range(0,parflag,1):
                process[i]=Process(target=execution,args=(mode,lock[parflag-i-1],mlock,com,opr,end[i],start[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],parflag-i,variable_region))
            for i in range(0,parflag,1):
                process[i].start()
            a='2'
            if len(ldata)==0:
                notlabelflag = 1
            if mode=='2':
                if notlabelflag==0:
                    while a!='esc':
                        a=input('process '+str(lstack[ltop.value])+' ')
                        mlock.acquire(False)
                        for i in range(0,parflag,1):
                            if int(lstack[ltop.value])==i+1:
                                lock[i].release()
                elif notlabelflag==1:
                    preprocess=0
                    while a!='esc':
                        endcount=0
                        a=input('process '+str(lstack[ltop.value])+' ')
                        mlock.acquire(False)
                        if int(rstack[rtop.value])!=0:
                            for i in range(0,parflag,1):
                                if int(rstack[rtop.value])==i+1:
                                    preprocess=i
                                    lock[i].release()
                        elif int(rstack[rtop.value])==0 and ((preprocess==0 and endflag[1].value==0) or (preprocess==1 and endflag[0].value==0)):
                            lock[preprocess].release()
                        elif (preprocess==0 and endflag[1].value==1) or (preprocess==1 and endflag[0].value==1):
                            if preprocess==0:
                                lock[1].release()
                            elif preprocess==1:
                                lock[0].release()
                                #for i in range(0,parflag,1):
                                #    if preprocess==i and endflag[parflag-i-1].value==0:
                                #        lock[preprocess].release()
                                #for i in range(0,parflag,1):
                                #    if preprocess==i and endflag[parflag-i-1].value==1:
                                #        lock[parflag-i-1].release()
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'

            elif mode=='1':
                if notlabelflag==0:
                    while a!='esc':
                        mlock.acquire()
                        ifflag=0
                        endcount=0
                        for i in range(0,parflag,1):
                            if (int(lstack[ltop.value])==i+1 and ifflag==0):
                                lock[i].release()
                                ifflag=1
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'
                elif notlabelflag==1:
                    preprocess=0
                    while a!='esc':
                        mlock.acquire()
                        ifflag=0
                        endcount=0
                        if int(rstack[rtop.value]!=0):
                            for i in range(0,parflag,1):
                                if (int(rstack[rtop.value])==i+1 and ifflag==0):
                                    preprocess=i
                                    lock[i].release()
                                    ifflag=1
                        elif int(rstack[rtop.value])==0 and ((preprocess==0 and endflag[1].value==0) or (preprocess==1 and endflag[0].value==0)):
                            lock[preprocess].release()
                        elif (preprocess==0 and endflag[1].value==1) or (preprocess==1 and endflag[0].value==1):
                            if preprocess==0:
                                lock[1].release()
                            elif preprocess==1:
                                lock[0].release()
                            #for i in range(0,parflag,1):
                            #    if preprocess==i and endflag[parflag-i-1].value==0:
                            #        lock[preprocess].release()
                            #for i in range(0,parflag,1):
                            #    if preprocess==i and endflag[parflag-i-1].value:
                            #        lock[parflag-i-1].release()
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'
            for i in range(0,parflag,1):
                process[i].join()
            execution(mode,lockfree,lockfree,com,opr,start[parflag-1]+1,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        elif parflag==0:
            execution(mode,lockfree,lockfree,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
    elif args[2]=='c':
        (start,end,variable_region)=coderead(start,end,variable_region)
        forward(ltop.value,rtop.value)
    elapsed_time = time.time()-start_time
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")