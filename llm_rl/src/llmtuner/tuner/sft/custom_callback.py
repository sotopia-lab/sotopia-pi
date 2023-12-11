import os
from transformers import TrainerCallback
from llmtuner.tuner.core.utils import is_first_node

class SaveModelCallback(TrainerCallback):
    
    def __init__(self, save_epochs, output_dir, checkpoint_saved_queue):
        self.save_epochs = save_epochs
        self.output_dir = output_dir
        self.checkpoint_saved_queue = checkpoint_saved_queue
        self.curr_epoch = 0
        
    def on_epoch_end(self, args, state, control, model=None, **kwargs):
        self.curr_epoch += 1
        if self.curr_epoch % self.save_epochs == 0:
            custom_checkpoint_name = f"checkpoint_epoch_{int(self.curr_epoch)}"
            output_dir = os.path.join(args.output_dir, custom_checkpoint_name)
            if getattr(model, "is_peft_model", True):
                model.save_pretrained(output_dir)
        control.should_save = False