var React = require('react');
var ReactDom = require('react-dom');
import {newfetch} from "./components"
import {Grid,Tab,Row,Table,Col,Radio} from "react-bootstrap"
const Dataset = React.createClass({
    contextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = this.context.store
        return {
            dataset:[] 
        };
    },
    componentDidMount() {
        newfetch("/data/").then(response=>{
            return response.json()
        }).then(response_json=>{
            this.setState({dataset:response_json.data})
        })
        this.store.addListener("dataset",this.datasetChange)
    },
    datasetChange(){
        console.log("datasetChange")
        this.forceUpdate()
    },
    onChange(evt){
        this.store.dispatch({"type":"dataset",
            data:evt.target.value})
    },
    componentWillUnmount: function() {
        this.store.removeListener("dataset",this.datasetChange)
        
    },
    render(){
        var storeState = this.store.getState()
        return <Grid>
            <Row className="show-grid">
      <Col xs={12} sm={12}>数据集列表</Col>
    </Row>
        <Row className="show-grid">
      <Col xs={12} sm={12}>
        <Table condensed responsive striped>
        <thead>
            <tr>
                <th>名称</th>
                <th>类型</th>
                <th>描述</th>
            </tr>
        </thead>
        <tbody>{this.state.dataset.map((data)=>{
            return <tr key={data.id}>
                <td>
                    <Radio onChange={this.onChange} 
                      inline 
                      name="dataset"
                      checked={storeState.dataset==data.id}
                      value={data.id}>
                      {data.name}
                    </Radio>
                </td>
                <td>{data.type}</td>
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

export default Dataset