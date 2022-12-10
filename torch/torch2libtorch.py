
import os
import torch




def build_model(checkpoint, input_shape):
    model = None
    model.load_state_dict(checkpoint)
    model.eval

    img = torch.zeros(input_shape).float()

    return model, img


def convert_script(
                 checkpoint_path,
                 input_shape,
                 output_file='tmp.pt',
                 ):

    checkpoint = torch.load(checkpoint_path, map_location='cpu')


    model, tensor_data = build_model(checkpoint, input_shape)
    print('model: ', model)
    print('input_data shape : ', tensor_data.size())
    with torch.jit.optimized_execution(True):
        trace_net = torch.jit.trace(model, tensor_data.float())
    trace_net.save(output_file)

    print(f'Successfully exported libtorch model: {output_file}')



if __name__ == '__main__':

    input_shape = (1, 3, 224, 224)


    simplify = True
    dynamic = True
    output_file = '../demo/libtorch.pt'

    checkpoint_file = '../demo/torch_model.pth'
    # convert model to libtorch file
    convert_script(
        checkpoint_file,
        input_shape,
        output_file=output_file,

    )
