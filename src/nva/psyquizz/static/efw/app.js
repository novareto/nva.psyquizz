webpackJsonp([1],{0:function(t,e,s){t.exports=s("NHnr")},NHnr:function(t,e,s){"use strict";Object.defineProperty(e,"__esModule",{value:!0});s("WgSQ"),s("y9m4"),s("+Mt+");var n=s("/5sW");s("n12u"),s("fx22"),s("gbyG"),s("Gh7F"),s("VjuZ");n["a"].directive("focus",{inserted:function(t){t.focus()}});var a={question:"",type:"",need_answers:!1,answers:[]};var i={methods:{showModal:function(){this.modalShown=!this.modalShown},delete_question:function(t){this.questions=this.questions.filter(function(e){return e!=t}),this.save_all()},save_all:function(){var t="";this.questions.forEach(function(e){if(e.need_answers){var s=[];e.answers.forEach(function(t){var e=t.value.trim();e.length>0&&s.push(e)}),t=e.question.trim()+" => "+e.type.trim()+"::"+s.join("::")}else t=e.question.trim()+" => "+e.type.trim();t+="\n"}),this.vv=t},remove_answer:function(t){this.question.answers=this.question.answers.filter(function(e){return e!=t})},may_need_answers:function(t){this.question.need_answers=["choice","multi"].includes(this.question.type),this.question.need_answers||(this.question.answers=[])},save_question:function(){var t=!1;if(this.question.question.trim()||(t=!0,alert("Please fill the question.")),this.question.type.trim()){if(this.question.need_answers){var e=[];this.question.answers.forEach(function(t){var s=t.value.trim();s.length&&e.push(s)}),e.length<2&&(alert("Please add at least 2 non-empty choices."),t=!0)}}else t=!0,alert("Please select a type of question.");t||(this.questions.push(Object.assign({},this.question)),this.question.question="",this.question.type="",this.question.needs_anwer=!1,this.question.answers=[],this.save_all())},add_answer:function(){this.question.answers.push(Object({value:""}))}},props:{questions:{type:String,default:""}},mounted:function(){console.log(this.questions),this.questions?(this.vv=this.questions,this.questions=JSON.parse(this.questions)):(this.vv="",this.questions=[])},data:function(){return{vv:"",modalShown:!1,question:a}}},o=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",[s("input",{attrs:{type:"hidden",name:"form.field.extra_questions"},domProps:{value:t.vv}}),t.questions.length>0?s("table",{staticClass:"table table-striped table-bordered"},[t._m(0),t._l(t.questions,function(e){return s("tr",{key:e.question},[s("td",[t._v(t._s(e.question))]),"choice"==e.type?s("td",[t._v("eine Antwort")]):t._e(),"multi"==e.type?s("td",[t._v("mehrere Antworten")]):t._e(),s("td",t._l(e.answers,function(e){return s("ul",{key:e.value},[s("li",[t._v(t._s(e.value))])])}))])})],2):t._e(),t.questions.length?t._e():s("button",{staticClass:"btn btn-default",attrs:{type:"button","data-toggle":"modal","data-target":"#extra_fields_widget"}},[t._v("\n    Zusatzfragen hinzufügen\n  ")]),t.questions.length?s("button",{staticClass:"btn btn-default",attrs:{type:"button","data-toggle":"modal","data-target":"#extra_fields_widget"}},[t._v("\n    Zusatzfragen bearbeiten\n  ")]):t._e(),s("div",{staticClass:"modal fade",class:{in:t.modalShown},attrs:{tabindex:"-1",role:"dialog",id:"extra_fields_widget"}},[s("div",{staticClass:"modal-dialog",attrs:{role:"document"}},[s("div",{staticClass:"modal-content"},[t._m(1),s("div",{staticClass:"modal-body"},[s("table",{staticClass:"table table-striped table-bordered"},[t._m(2),t._l(t.questions,function(e){return s("tr",{key:e.question},[s("td",[t._v(t._s(e.question))]),"choice"==e.type?s("td",[t._v("eine Antwort")]):t._e(),"multi"==e.type?s("td",[t._v("mehrere Antworten")]):t._e(),s("td",t._l(e.answers,function(e){return s("ul",{key:e.value},[s("li",[t._v(t._s(e.value))])])})),s("td",[s("a",{on:{click:function(s){t.delete_question(e)}}},[t._v("löschen")])])])})],2),s("form",{on:{submit:function(e){e.preventDefault(),t.save_question()}}},[s("div",{staticClass:"form-group"},[s("label",{attrs:{for:"frage"}},[t._v("Frage")]),s("input",{directives:[{name:"model",rawName:"v-model",value:t.question.question,expression:"question.question"}],ref:"frage",staticClass:"form-control",attrs:{type:"text",placeholder:"Bitte geben Sie hier Ihre Frage ein"},domProps:{value:t.question.question},on:{input:function(e){e.target.composing||t.$set(t.question,"question",e.target.value)}}})]),s("div",{staticClass:"form-group"},[s("label",{attrs:{for:"format"}},[t._v("Antwortformat")]),s("select",{directives:[{name:"model",rawName:"v-model",value:t.question.type,expression:"question.type"}],staticClass:"form-control",attrs:{id:"format"},on:{change:[function(e){var s=Array.prototype.filter.call(e.target.options,function(t){return t.selected}).map(function(t){var e="_value"in t?t._value:t.value;return e});t.$set(t.question,"type",e.target.multiple?s:s[0])},t.may_need_answers]}},[s("option",{attrs:{value:"choice",selected:"selected"}},[t._v("\n\t\t  nur eine Antwort möglich\n\t\t")]),s("option",{attrs:{value:"multi"}},[t._v("mehrere Antworten möglich")])])]),t.question.need_answers?s("div",{staticClass:"form-group"},[s("label",{attrs:{for:"antworten"}},[t._v("Antworten")]),t._l(t.question.answers,function(e){return s("div",{key:e},[s("input",{directives:[{name:"model",rawName:"v-model",value:e.value,expression:"answer.value"},{name:"focus",rawName:"v-focus"}],domProps:{value:e.value},on:{input:function(s){s.target.composing||t.$set(e,"value",s.target.value)}}}),s("button",{staticClass:"btn btn-default",on:{click:function(s){s.preventDefault(),t.remove_answer(e)}}},[s("span",{staticClass:"glyphicon glyphicon-remove",attrs:{"aria-hidden":"true"}})])])}),s("button",{staticClass:"btn btn-default",attrs:{type:"submit"},on:{click:function(e){return e.preventDefault(),t.add_answer(e)}}},[t._v("\n\t\tAntwort hinzufügen\n\t      ")])],2):t._e(),s("hr"),t._m(3)])]),t._m(4)])])])])},r=[function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("tr",[s("th",[t._v("Frage")]),s("th",[t._v("Typ")]),s("th",[t._v("Antwort(en)")])])},function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",{staticClass:"modal-header"},[s("button",{staticClass:"close",attrs:{type:"button","data-dismiss":"modal","aria-label":"Close"}},[s("span",{attrs:{"aria-hidden":"true"}},[t._v("×")])]),s("h4",{staticClass:"modal-title"},[t._v("Zusatzfrage erfassen")])])},function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("tr",[s("th",[t._v("Frage")]),s("th",[t._v("Typ")]),s("th",[t._v("Antwort(en)")]),s("th")])},function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",[s("button",{staticClass:"btn btn-default",attrs:{type:"submit"}},[t._v("\n\t\tFrage Speichern\n\t      ")])])},function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",{staticClass:"modal-footer"},[s("button",{staticClass:"btn btn-default",attrs:{type:"button","data-dismiss":"modal"}},[t._v("Schließen")])])}],u=s("XyMi");function l(t){s("Vdop")}var c=!1,d=l,v="data-v-ef37ca28",f=null,h=Object(u["a"])(i,o,r,c,d,v,f),m=h.exports,_=s("PXmv");s("CLCt");n["a"].use(_["a"]),n["a"].config.productionTip=!1,n["a"].config.ignoredElements=["extra-fields-widget"],n["a"].customElement("extra-fields-widget",m,{})},Vdop:function(t,e){}},[0]);