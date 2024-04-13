import os
from glob import glob

import zerohertzLib as zz
from tqdm import tqdm

JENKINS = zz.util.Json("JENKINS.json")

if __name__ == "__main__":
    logger = zz.logging.Logger("JENKINS CREDENTIAL")
    for log in tqdm(
        glob(os.path.join(JENKINS["PVC"], "jobs", "*", "*", "*", "*", "*", "log"))
    ):
        with open(log, "r") as file:
            tmp = file.readlines()
        tmp = "".join(tmp)
        for crd in JENKINS["CREDENTIAL"]:
            if crd in tmp:
                logger.warning(log)
                logger.warning(tmp)
