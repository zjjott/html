var React = require('react');
var ReactDom = require('react-dom');
import {newfetch} from "./components"
import {Grid,Tab,Row,Table,Col,Radio} from "react-bootstrap"


const MethodList = React.createClass({
    contextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = this.context.store
        return {
            methods:[] 
        };
    },
    componentDidMount() {
        newfetch("/task/method/?public=true&trained=false").then(response=>{
            return response.json()
        }).then(response_json=>{
            this.setState({methods:response_json.data})
        })
        this.store.addListener("method",this.methodChange)
    },
    methodChange(){
        this.forceUpdate()
    },
    onChange(evt){
        this.store.dispatch({"type":"method",
            data:evt.target.value})
    },
    componentWillUnmount: function() {
        this.store.removeListener("method",this.methodChange)
        
    },
    render(){
        var storeState = this.store.getState()
        return <Grid>
            <Row className="show-grid">
      <Col xs={12} sm={12}>模型列表</Col>
    </Row>
        <Row className="show-grid">
      <Col xs={12} sm={12}>
        <Table condensed responsive striped>
        <thead>
            <tr>
                <th>名称</th>
                <th>描述</th>
            </tr>
        </thead>
        <tbody>{this.state.methods.map((data)=>{
            return <tr key={data.id}>
                <td>
                    <Radio onChange={this.onChange} 
                      inline 
                      name="methods"
                      checked={storeState.method==data.id}
                      value={data.id}>
                      {data.name}
                    </Radio>
                </td>
                <td>{data.description}</td>
            </tr>
        })}
        </tbody>
        </Table>
      </Col>
    </Row>
    </Grid>

    }
})

export default MethodList