var React = require('react');
var ReactDom = require('react-dom');
import {newfetch} from "./components"
import {Grid,Tab,Row,Table,Col,Radio} from "react-bootstrap"

const DatasetPreview = React.createClass({
    getInitialState: function() {
        return {
            data:[],
            data_id:this.props.data_id,
            length:0,
            meta:null
        };
    },
    componentWillReceiveProps(nextProps) {
        if(nextProps.data_id!=this.state.data_id){
            this.setState({data_id:nextProps.data_id},
                this.loadDataset)
        }
    },
    loadDataset(){
        newfetch(`/data/${this.state.data_id}/`).then(
            response=>{
            return response.json()
        }).then(response_json=>{
            this.setState({data:response_json.data,
                meta:response_json.meta})
        })
    },
    componentDidMount: function() {
        if(this.state.data_id){
            this.loadDataset()
        }
    },
    render(){
        return <Row className="show-grid">
        {this.state.meta?<Col xs={12} sm={12}>
        数据集预览,显示第{this.state.meta.offset}~{
            this.state.meta.limit+this.state.meta.offset}条，共{this.state.meta.total}条</Col>:null
      }
      <Col xs={12} sm={12}>
        <Table condensed responsive striped>
        {this.state.meta?<thead>
            <tr>
            {this.state.meta.headers.map((header,index)=>{
                return <th key={index}>{header}</th>
            })}
            </tr>
        </thead>:null}
        
        <tbody>{this.state.data.map((row,index)=>{
            return <tr key={index}>
            {row.map((col,i)=>{
                return <td key={`${index}.${i}`}>
                    {col}
                </td>
            })}
            </tr>
        })}
        </tbody>
        </Table>
      </Col>

    </Row>
    }
})
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
    <DatasetPreview data_id={storeState.dataset} />
    </Grid>

    }
})

export default Dataset