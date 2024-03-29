import itertools
import subprocess
import time
from mcli.sdk import RunConfig, create_run, wait_for_run_status

 # if not autoresume else 'my-cool-autoresume'
gpu_num=8 # 1
cluster='r1z1'
images = ['mosaicml/pytorch:2.0.1_cu118-python3.10-ubuntu20.04'] #, 'mosaicml/pytorch:1.13.1_cu117-python3.10-ubuntu20.04']
composer_versions = ['v0.18.1'] # ['v0.13.5', 'v0.14.0', 'v0.14.1', 'v0.15.0',  'v0.16.0']


manual_test_integration = {
    'integration_type': 'git_repo',
    'git_repo': 'eracah/composer-test-ckpts',
    'git_branch': 'master',
    'path': '/tmp/composer-test-ckpts'
}

fsdp_state_dict_types = ['sharded', 'full']
precisions = ['amp_fp16', 'amp_bf16']
sharding_strategies = ['SHARD_GRAD_OP', 'FULL_SHARD']

for fsdp_state_dict_type, precision, sharding_strategy, image, composer_version in itertools.product(fsdp_state_dict_types,
                                                                            precisions,
                                                                            sharding_strategies, images, composer_versions):
    composer_integration = {
        'integration_type': 'git_repo',
        'git_repo': 'mosaicml/composer',
        'git_branch': f'{composer_version}',
        'pip_install': '-e .[all]',
        'path': '/tmp/composer'
    }

    integrations = [manual_test_integration, composer_integration]
    pt_version = image.split(':')[1].split('_')[0]
    cmd = f'pip install pydantic==1.10.12; cd /tmp/composer-test-ckpts && composer -n 2 make_test_ckpt.py {fsdp_state_dict_type} {precision} {sharding_strategy}'
   
    run_name = f"bcompat-{fsdp_state_dict_type}-{precision.split('_')[-1]}-pt-{pt_version.replace('.', '-')}-cp-{composer_version.replace('.', '-')}"
    print(run_name)
    cfg = RunConfig(
        name=run_name,
        gpu_num=gpu_num,
        cluster=cluster,
        image=image,
        integrations=integrations,
        command=cmd,
        scheduling={'priority': 'highest'}
    )
    run = create_run(cfg)
