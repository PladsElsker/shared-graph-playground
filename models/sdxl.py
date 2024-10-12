from diffusers import StableDiffusionXLPipeline
import torch


device = 'meta'
pipeline = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant='fp16', use_safetensors=True,
)
pipeline.to(device)


def model(input_image, prompt='Astronaut in a jungle, cold color palette, muted colors, detailed, 8k'):
    input_image = input_image.to(device)
    tokens = pipeline.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    embs = pipeline.text_encoder.to(device)(**tokens)
    embs2 = pipeline.text_encoder_2.to(device)(**tokens)
    
    encoder_hidden_states = torch.cat([embs.last_hidden_state, embs2.last_hidden_state], dim=-1)
    time_ids = get_add_time_ids(torch.tensor([input_image.shape[2]*8, input_image.shape[3]*8], device=device).unsqueeze(-1), torch.tensor([0, 0], device=device).unsqueeze(-1))
    pipeline.unet.to(device)
    ret = pipeline.unet(input_image, 1, encoder_hidden_states, added_cond_kwargs={
        'text_embeds': embs.pooler_output,
        'time_ids':  time_ids,
    })

    return ret.sample


def get_add_time_ids(original_size, crops_coords_top_left):
    add_time_ids = torch.cat([
        original_size,
        crops_coords_top_left,
        torch.tensor([[1024]*2], device=original_size.device).expand(len(original_size), -1),
    ], dim=1)

    return add_time_ids
