import shell_util as exec_cmd
import subprocess
import json
import zlib
import sys
import os

nvm_attr_list = [
    "ppwrite",
    "ownerwrite",
    "authwrite",
    "policywrite",
    "policy_delete",
    "writelocked",
    "writeall",
    "writedefine",
    "write_stclear",
    "globallock",
    "ppread",
    "ownerread",
    "authread",
    "policyread",
    "no_da",
    "orderly",
    "clear_stclear",
    "readlocked",
    "written",
    "platformcreate",
    "read_stclear",
]

nvm_predefined_index = ["0x1c00002", "0x1c0000a", "0x1c00016"]

tpm2_max_auth_fail = None
tpm2_lockout_interval = None
tpm2_lockout_recovery = None
client_log = None


class TPM:
    def __init__(
        self,
        nvm_index,
        owner_val,
        nvm_data,
        binary_file,
        nv_auth_val,
        nvm_size,
        nvm_attr,
    ):
        self.nvm_index = nvm_index
        self.owner_val = owner_val
        self.nvm_data = nvm_data
        self.binary_file = binary_file
        self.nv_auth_val = nv_auth_val
        self.nvm_attr = nvm_attr
        self.nvm_size = nvm_size
        self.nvm_offset = "0"
        self.rng_input = "16"
        self.Check_IFX_TPM()
        self.OnStart()
        # self.OnClear()
        # self.OnGetCapVar()
        self.OnChangeAuth()
        self.OnGetCapVar()

    def OnGetCapVar(self):
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_getcap",
                "properties-variable",
            ]
        )
        # print(str(command_output))
        print("'tpm2_getcap properties-variable' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnStart(self):
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_startup",
                "-c",
            ]
        )
        print(str(command_output))
        print(("'tpm2_startup -c' executed \n"))

    def OnChangeAuth(self):
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_changeauth",
                "-c",
                "owner",
                exec_cmd.ownerAuth,
            ]
        )
        print(str(command_output))
        print("'tpm2_changeauth -c owner " + exec_cmd.ownerAuth + "' executed \n")
        if exec_cmd.endorseAuth != "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_changeauth",
                    "-c",
                    "endorsement",
                    exec_cmd.endorseAuth,
                ]
            )
            print(str(command_output))
            print(
                "'tpm2_changeauth -c endorsement "
                + exec_cmd.endorseAuth
                + "' executed \n"
            )
        if exec_cmd.lockoutAuth != "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_changeauth",
                    "-c",
                    "lockout",
                    exec_cmd.lockoutAuth,
                ]
            )

            print(str(command_output))
            print(
                "'tpm2_changeauth -c lockout " + exec_cmd.lockoutAuth + "' executed \n"
            )

    def OnNVDefine(self):

        assert self.nvm_size.isdigit(), "nvm_size must be an integer"
        assert int(self.nvm_size) <= 2048, "Maximum NVM size is 2048. Input Again.\n"
        nvm_size = int(self.nvm_size)
        nvm_attr = self.nvm_attr
        temp_attr = []
        for value in nvm_attr:
            temp_attr.append(value)
        if (self.nvm_index == 0) | (nvm_size == 0):
            return
        nvm_attr = "|".join(temp_attr)
        print("Attributes are: " + nvm_attr + "\n")
        # if (self.owner_input.GetValue()=="" and self.nv_auth_input.GetValue()==""):
        # self.right_txt_display.AppendText("Owner Authorisation and NV Authorisation Empty. Input Again.\n")
        # return

        # if NV field is empty
        if self.nv_auth_val == "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvdefine",
                    self.nvm_index,
                    "-C",
                    "o",
                    "-s",
                    self.nvm_size,
                    "-a",
                    nvm_attr,
                    "-P",
                    self.owner_val,
                ]
            )

        # if NV field is specified
        elif self.nv_auth_val != "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvdefine",
                    self.nvm_index,
                    "-C",
                    "o",
                    "-s",
                    self.nvm_size,
                    "-a",
                    nvm_attr,
                    "-P",
                    self.owner_val,
                    "-p",
                    self.nv_auth_val,
                ]
            )

        print(str(command_output))
        print("'tpm2_nvdefine' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def Check_IFX_TPM(self):
        cmd = " ls /dev/tpm0"
        ps_command = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        command_output = ps_command.stdout.read()
        retcode = ps_command.wait()
        if command_output.decode() != "/dev/tpm0\n":
            print("device not found!")
            return

        cmd = " tpm2_getcap properties-fixed | grep -A2 'MANUFACTURER' | grep value | grep -Eo '[A-Z]*'"
        ps_command = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        command_output = ps_command.stdout.read()

        retcode = ps_command.wait()
        print(command_output.decode())

    def OnClear(self):
        command_output = exec_cmd.execTpmToolsAndCheck(["tpm2_clear", "-c", "p"])
        exec_cmd.createProcess("sudo rm *.tss", None)
        print(str(command_output))
        print("'tpm2_clear -c p' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnGenRNG(self):
        rand_num = 0
        no_bytes = self.rng_input
        assert no_bytes.isdigit(), "Number of bytes is not an integer, try again."
        no_bytes = abs(int(no_bytes))
        print(no_bytes)
        # assuming output type is hex
        command_output = exec_cmd.execCLI(
            [
                "openssl",
                "rand",
                "-engine",
                "tpm2tss",
                "-hex",
                str(no_bytes),
            ]
        )
        split_output = command_output.split("\n")
        for value in split_output:
            if len(value.lower()) == no_bytes * 2:
                rand_num = value
                print("Random Number: " + rand_num + "\n")

        print("'openssl rand -engine tpm2tss -hex " + str(no_bytes) + "' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")
        return rand_num

    def OnNVWrite(self):
        nvm_index = self.nvm_index
        owner_val = self.owner_val
        nv_auth_val = self.nv_auth_val
        nvm_data = compressed_data = ""
        with open(self.binary_file, "r") as f:
            json_data = json.load(f)
            nvm_data = json.dumps(json_data)
            # print("before", sys.getsizeof(nvm_data))
            compressed_data = zlib.compress(nvm_data.encode())
            # print("after:", sys.getsizeof(compressed_data))
        assert (nvm_index != 0) and (
            nvm_data != "" and len(compressed_data) <= 2048
        ), "nvm_index or nvm_data cannot be 0 or nvm_data cannot be greater than 2048 bytes"
        with open("nvm_data.gz", "wb") as f:
            f.write(compressed_data)
            f.close()

        # if NV auth field is empty
        if nv_auth_val == "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvwrite",
                    nvm_index,
                    "-C",
                    "o",
                    "-i",
                    "nvm_data.gz",
                    "-P",
                    owner_val,
                ]
            )

        # if NV auth field is specified
        elif nv_auth_val != "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvwrite",
                    nvm_index,
                    "-i",
                    "nvm_data.gz",
                    "-P",
                    nv_auth_val,
                ]
            )

        print(str(command_output))
        print("'tpm2_nvwrite' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnNVRelease(self):
        nvm_index = self.nvm_index
        owner_val = self.owner_val
        if nvm_index == 0:
            return
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_nvundefine",
                "-C",
                "o",
                "-P",
                owner_val,
                nvm_index,
            ]
        )
        print(str(command_output))
        print("'tpm2_nvrelease' executed \n")

    def OnNVRead(self):
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

        nvm_index = self.nvm_index
        nvm_size = self.nvm_size
        owner_val = self.owner_val
        nv_auth_val = self.nv_auth_val
        nvm_offset = self.nvm_offset
        read_size = 2048
        json_str = ""

        assert (
            isinstance(nvm_size, str)
            and isinstance(nvm_offset, str)
            and isinstance(read_size, int)
        ), "Offset or size is an invalid value (not an integer)."
        assert read_size > 0, "read size cannot be 0 or negative."

        # if NV auth field is empty
        if nv_auth_val == "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvread",
                    nvm_index,
                    "-C",
                    "o",
                    "-s",
                    str(read_size),
                    "-o",
                    nvm_offset,
                    "-P",
                    owner_val,
                    "-o",
                    "nvdata.gz",
                ]
            )

        # if NV auth field is specified
        elif nv_auth_val != "":
            command_output = exec_cmd.execTpmToolsAndCheck(
                [
                    "tpm2_nvread",
                    nvm_index,
                    "-s",
                    str(read_size),
                    "-o",
                    nvm_offset,
                    "-P",
                    nv_auth_val,
                    "-o",
                    "nvdata.gz",
                ]
            )

        if command_output.find("ERROR") != -1:
            print(str(command_output) + "\n")
            return

        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "xxd",
                "nvdata.gz",
            ]
        )
        with open(
            "/home/pi/optiga-tpm-explorer/TPM_python/working_space/nvdata.gz", "rb"
        ) as f:
            compressed_data = f.read()
            json_str = zlib.decompress(compressed_data).decode()
            f.close()
        with open("/home/pi/optiga-tpm-explorer/TPM_python/data/output.json", "w") as f:
            json.dump(json.loads(json_str), f)
            f.close()

        print("'tpm2_nvread' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnList(self):
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_getcap",
                "handles-persistent",
            ]
        )
        print(str(command_output))
        print("'tpm2_getcap handles-persistent' executed \n")
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnCreatePrimary(self):
        if os.path.exists(os.path.join("./working_space", "RSAprimary.ctx")):
            exec_cmd.execTpmToolsAndCheck(["rm", "RSAprimary.ctx"])
        output_message = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_createprimary",
                "-C",
                "o",
                "-P",
                exec_cmd.ownerAuth,
                "-g",
                "sha256",
                "-G",
                "rsa",
                "-c",
                "RSAprimary.ctx",
            ]
        )
        # print("first output :", str(output_message) + "\n")
        # self.Update()
        output_message = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_evictcontrol",
                "-C",
                "o",
                "-c",
                "RSAprimary.ctx",
                "-P",
                exec_cmd.ownerAuth,
                "0x81000004",
            ]
        )
        # print("second output",str(output_message) + "\n")
        print(
            "tpm2_createprimary -C o -P "
            + exec_cmd.ownerAuth
            + " -g sha256 -G rsa -c RSAprimary.ctx\n"
        )
        print(
            "tpm2_evictcontrol -C o -c RSAprimary.ctx -P "
            + exec_cmd.ownerAuth
            + " 0x81000004\n"
        )
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnEvict(self, handle):
        specific_handle = handle
        command_output = exec_cmd.execTpmToolsAndCheck(
            [
                "tpm2_evictcontrol",
                "-C",
                "o",
                "-c",
                specific_handle,
                "-P",
                exec_cmd.ownerAuth,
            ]
        )
        print(
            "'tpm2_evictcontrol -C o -c "
            + specific_handle
            + " -P "
            + exec_cmd.ownerAuth
            + "' executed \n"
        )
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnGenKeyPair(self):
        assert exec_cmd.ownerAuth != "", "Owner password is not set"
        file_names = [
            "rsa2.tss",
            "rsa2.pub",
            "mycipher",
            "mysig",
        ]

        # Iterate over the list of file names
        for file_name in file_names:
            file_path = os.path.join('"./working_space"', file_name)
            if os.path.exists(file_path):
                exec_cmd.execTpmToolsAndCheck(["rm", file_name])
        command_output = exec_cmd.execCLI(
            [
                "tpm2tss-genkey",
                "-o",
                exec_cmd.ownerAuth,
                "-a",
                "rsa",
                "rsa2.tss",
            ]
        )
        print(str(command_output))
        print("'tpm2tss-genkey -a rsa rsa2.tss' executed \n")
        command_output = exec_cmd.execCLI(
            [
                "openssl",
                "rsa",
                "-engine",
                "tpm2tss",
                "-inform",
                "engine",
                "-in",
                "rsa2.tss",
                "-pubout",
                "-outform",
                "pem",
                "-out",
                "rsa2.pub",
            ]
        )
        print(
            "'openssl rsa -engine tpm2tss -inform engine -in rsa2.tss -pubout -outform pem -out rsa2.pub' executed \n"
        )
        print("rsa.tss contains: \n")
        filehandle = open("rsa2.tss", "r")
        print(filehandle.read() + "\n")
        filehandle.close()
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnEnc(self):
        self.data_input = "test1234"
        assert self.data_input != "", "Input data is not set"
        input_data = self.data_input
        data_file = open("engine_data.txt", "w")
        data_file.write(input_data)
        data_file.close()
        exec_cmd.execCLI(
            [
                "openssl",
                "pkeyutl",
                "-pubin",
                "-inkey",
                "rsa2.pub",
                "-in",
                "engine_data.txt",
                "-encrypt",
                "-out",
                "mycipher",
            ]
        )
        print(
            "'openssl pkeyutl -pubin -inkey rsa2.pub -in engine_data.txt -encrypt -out mycipher' executed \n"
        )
        print("mycipher contains:")
        command_output = exec_cmd.execCLI(
            [
                "xxd",
                "mycipher",
            ]
        )
        print(command_output)
        print("++++++++++++++++++++++++++++++++++++++++++++\n")

    def OnDec(self):
        f = open("temp.conf", "w+")
        f.write(exec_cmd.openssl_cnf)
        f.close()

        cmd = "OPENSSL_CONF=temp.conf openssl pkeyutl -engine tpm2tss -keyform engine -inkey rsa2.tss -decrypt -in mycipher"
        ps_command = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        command_output = ps_command.stdout.read()
        retcode = ps_command.wait()

        print(str(command_output.decode()))
        print(
            "OPENSSL_CONF=temp.conf openssl pkeyutl -engine tpm2tss -keyform engine -inkey rsa2.tss -decrypt -in mycipher' executed \n"
        )
        print("++++++++++++++++++++++++++++++++++++++++++++\n")
        return command_output.decode()


if __name__ == "__main__":
    exec_cmd.checkDir()
    tpm = TPM(
        nvm_index="0x1500016",
        owner_val="owner123",
        nvm_data="",
        binary_file="/home/pi/optiga-tpm-explorer/TPM_python/data/tmp.json",
        nv_auth_val="nv123",
        nvm_size="2048",
        nvm_attr=["authread", "authwrite"],
    )
    # tpm.OnClear()
    # tpm.OnGenRNG() ---- done
    # tpm.OnNVDefine() --- done
    # tpm.OnNVWrite() --- done
    # tpm.OnNVRead() --- done
    # tpm.OnCreatePrimary()
    # tpm.OnGenKeyPair() --- done
    # tpm.OnEnc() --- done
    # tpm.OnDec() --- done
