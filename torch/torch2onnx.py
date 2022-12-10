import onnx
import os
import torch



def build_model(checkpoint, input_shape):
    model = None
    model.load_state_dict(checkpoint)
    model.eval

    img = torch.zeros(input_shape).float()

    return model, img


def pytorch2onnx(
                 checkpoint_path,
                 input_shape,
                 opset_version=11,
                 output_file='tmp.onnx',
                 simplify = True,
                 dynamic = True,
                 ):

    checkpoint = torch.load(checkpoint_path, map_location='cpu')


    model, tensor_data = build_model(checkpoint, input_shape)
    print('model: ', model)
    print('input_data shape : ', tensor_data.size())


    if simplify or dynamic:
        ori_output_file = output_file.split('.')[0]+"_ori.onnx"
    else:
        ori_output_file = output_file

    # Define input and outputs names, which are required to properly define
    # dynamic axes
    input_names = ['input']
    output_names = ['output']


    # Define dynamic axes for export
    dynamic_axes = None
    if dynamic:
        dynamic_axes = {out: {0: '?'} for out in output_names}
        dynamic_axes[input_names[0]] = {
            0: '?',
            2: '?',
            3: '?'
        }

    torch.onnx.export(
        model,
        tensor_data,
        ori_output_file,
        keep_initializers_as_inputs=False,
        verbose=False,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        opset_version=opset_version)

    if simplify or dynamic:
        model = onnx.load(ori_output_file)
        if simplify:
            from onnxsim import simplify
            #print(model.graph.input[0])
            if dynamic:
                input_shapes = {model.graph.input[0].name : list(input_shape)}
                model, check = simplify(model, input_shapes=input_shapes, dynamic_input_shape=True)
            else:
                model, check = simplify(model)
            assert check, "Simplified ONNX model could not be validated"
        onnx.save(model, output_file)
        os.remove(ori_output_file)

    print(f'Successfully exported ONNX model: {output_file}')



if __name__ == '__main__':

    opset_version = 11
    input_shape = (1, 3, 224, 224)


    simplify = True
    dynamic = True
    output_file = '../demo/model2onnx.onnx'

    checkpoint_file = '../demo/torch_model.pth'
    # convert model to onnx file
    pytorch2onnx(
        checkpoint_file,
        input_shape,
        opset_version=opset_version,
        output_file=output_file,
        simplify = simplify,
        dynamic = dynamic
    )
