import json
import time
import os
import multiprocessing as mlp
from tqdm import tqdm

cmdline = "vina --maps ../protein/FEN1 --force_even_voxels --dir /tmp/ --scoring ad4 --seed 181129 --max_step 20 --exhaustiveness 128 --num_modes 1  --verbosity 0 --max_gpu_memory 31000"



def calc(ntorsions, natoms, nt, ns, cmd, filename):
    print("entering calc", ntorsions, natoms, nt, ns)
    
    dirname = cmd.split("--dir ")[1].split(" ")[0]
    os.makedirs(dirname, exist_ok=True)
    result = []

    batch_size = int((30000.0-20017.0)/(1.214869+0.0038522*nt+0.011978*natoms*natoms) * 0.6)
    print("batch size=", batch_size)

    cmd = cmd.replace("--seed 181129", "--seed 1")
    cmd = cmd.replace("--exhaustiveness 128", "--exhaustiveness {}".format(nt))
    cmd = cmd.replace("--max_step 20", "--max_step {}".format(ns))
    cmd = cmd.replace("--dir nt128-ns20/", "--dir nt{}-ns{}/".format(nt, ns))
    cmd += " --gpu_batch"
    for i in range(batch_size):
        cmd += " " + filename
    print(cmd[:200])
    with open("current_run.sh", "w") as f:
        f.write(cmd)
    try:
        st = time.time()
        status = os.system("bash current_run.sh")
        exit_code = os.waitstatus_to_exitcode(status)
        assert(exitcode == 0)
        # print(cmd)
        spendtime = time.time()-st
        if os.path.exists("{}/{}_out.pdbqt".format(dirname, filename[:-6])):
            with open("{}/{}_out.pdbqt".format(dirname, filename[:-6]), "r") as f:
                f.readline()
                score = float(f.readline().split()[3])
            result.append([nt, ns, natoms, ntorsions, spendtime/batch_size])
        else:
            result.append([nt, ns, natoms, ntorsions, 99999])
        return result
    except AssertionError:
        print(cmd)
    except:
        return [[]]

def run_speed_test(nt, ns):
    info = []
    cnt = 0
    for natom in range(15,39):
        for ntorsion in range(0, 14):
            filename = "na" + str(natom) + "-nt" + str(ntorsion) + ".pdbqt"
            if os.path.isfile(filename):
                cnt = cnt + 1
                if cnt % 5 != 0:
                    continue
                info.extend(calc(ntorsion, natom, nt, ns, cmdline, filename))

    os.makedirs("../results-ad4", exist_ok=True)
    with open("../results-ad4/nt" + str(nt) + "-ns" + str(ns) + ".csv", "w") as f:
        f.write("nt,ns,natoms,ntorsions,time\n")
        f.write("\n".join(["{},{},{},{},{}".format(*x) for x in info]))

os.chdir("pdbqt")
for nt,ns in tqdm([
    # [128, 15], [128, 20], [256, 15],
    # [512, 20], [1024, 20],
    # [512, 30], [1024, 30], [2048, 20],
    # [256, 40], [265, 50], [128, 40], [128, 50]
    # [128, 100], [256, 100], [128, 120], [256, 120], [512, 60], [512, 80]
    # [128,20], 
    [384,40], [512,40]
]):
    
    run_speed_test(nt,ns)
