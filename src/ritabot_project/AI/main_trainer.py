# -*- coding: utf-8 -*-

import trainer
import sys
language=str(sys.argv[1])
id_user=str(sys.argv[2])
id_agent=str(sys.argv[3])
data="data.json"
t=trainer.training().prepare_data_trainer(language,data,id_user,id_agent)

#t=trainer.training().prepare_data_trainer('english','trainer_data_1.json',123,2)


