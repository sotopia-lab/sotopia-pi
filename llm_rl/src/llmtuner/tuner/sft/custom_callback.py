import os
from transformers import TrainerCallback
from llmtuner.tuner.core.utils import is_first_node

class SaveModelCallback(TrainerCallback):
    def __init__(self, save_epochs, output_dir, checkpoint_saved_queue, improve_step):
        self.save_epochs = save_epochs
        self.output_dir = output_dir
        self.checkpoint_saved_queue = checkpoint_saved_queue
        self.curr_improve_step = improve_step
        self.curr_epoch = 0
        
    def on_epoch_end(self, args, state, control, model=None, **kwargs):
        self.curr_epoch += 1
        if self.curr_epoch % self.save_epochs == 0:
            control.should_save = True
        else:
            control.should_save = False
    
    def on_save(self, args, state, control, model, **kwargs):
        # # Only save the model on the first node
        if not is_first_node():
            return
        
        # Customized checkpoint name
        custom_checkpoint_name = f"checkpoint_improve-{self.curr_improve_step}_epoch-{int(self.curr_epoch)}"
        
        # Original auto-saved checkpoint directory
        auto_checkpoint_dir = os.path.join(args.output_dir, f"checkpoint-{state.global_step}")
        
        # Destination directory for the custom checkpoint
        custom_checkpoint_dir = os.path.join(self.output_dir, custom_checkpoint_name)
        
        # Rename the auto-saved checkpoint directory
        os.rename(auto_checkpoint_dir, custom_checkpoint_dir)

        # Write the custom checkpoint name to the deploy queue
        with open(self.checkpoint_saved_queue, 'a') as f:
            f.write(f"{custom_checkpoint_name}\n")