var React = require('react');
var ReactDom = require('react-dom');
import {FieldGroup} from "react-bootstrap"
const InputGroup = React.createClass({
    getInitialState: function() {
        return {
        };
    },
    render(){
        return <input
                  id="formControlsFile"
                  type="file"
                  name={this.props.name}
                  label="用于预测的文件"
                />
    }
})
export default InputGroup
