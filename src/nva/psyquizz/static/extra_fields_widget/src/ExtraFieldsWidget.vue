<template>
<div>
  <input type="hidden" name="form.field.extra_questions" v-bind:value="vv">
  <table class="table table-striped table-bordered" v-if="questions.length > 0">
    <tr>
      <th>Frage</th>
      <th>Typ</th>
      <th>Antwort(en)</th>
    </tr>
    <tr v-for="q in questions" :key="q.question">
      <td>{{q.question}}</td>
      <td v-if="q.type=='choice'">eine Antwort</td>
      <td v-if="q.type=='multi'">mehrere Antworten</td>
      <td>
	<ul v-for="a in q.answers" :key="a.value">
	  <li>{{a.value}}</li>
	</ul>
      </td>
    </tr>
  </table>

  <button type="button" class="btn btn-default" v-if="!questions.length"
          data-toggle="modal" data-target="#extra_fields_widget">
    Zusatzfragen hinzufügen
  </button>
  <button type="button" class="btn btn-default" v-if="questions.length"
          data-toggle="modal" data-target="#extra_fields_widget">
    Zusatzfragen bearbeiten
  </button>

  <div class="modal fade" tabindex="-1" role="dialog"
       id="extra_fields_widget" :class="{ in: modalShown }">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
	<div class="modal-header">
	  <button type="button" class="close"
                  data-dismiss="modal" aria-label="Close">
	    <span aria-hidden="true">&times;</span>
	  </button>
	  <h4 class="modal-title">Zusatzfrage erfassen</h4>
	</div>
	<div class="modal-body">
	  <table class="table table-striped table-bordered">
	    <tr>
	      <th>Frage</th>
	      <th>Typ</th>
	      <th>Antwort(en)</th>
	      <th></th>
	    </tr>
	    <tr v-for="q in questions" :key="q.question">
	      <td>{{q.question}}</td>
	      <td v-if="q.type=='choice'">eine Antwort</td>
	      <td v-if="q.type=='multi'">mehrere Antworten</td>
	      <td>
		<ul v-for="a in q.answers" :key="a.value">
		  <li>{{a.value}}</li>
		</ul>
	      </td>
	      <td>
		<a v-on:click="delete_question(q)">löschen</a>
	      </td>
	    </tr>
	  </table>
          
	  <form @submit.prevent="save_question()">
	    <div class="form-group">
	      <label for="frage">Frage</label>
	      <input v-model="question.question" type="text"
                     class="form-control" ref="frage"
                     placeholder="Bitte geben Sie hier Ihre Frage ein" />
	    </div>
	    <div class="form-group">
	      <label for="format">Antwortformat</label>
	      <select v-model="question.type"
                      class="form-control" id="format">
		<option value="choice" selected="selected">
		  nur eine Antwort möglich
		</option>
		<option value="multi">mehrere Antworten möglich</option>
		<!-- <option value="bool">Wahr oder Falsch</option> -->
	      </select>
	    </div>
	    <div class="form-group">
	      <label for="antworten">Antworten</label>
	      <div v-for="answer in question.answers" v-bind:key="answer">
		<input v-model="answer.value" v-focus />
		<button class="btn btn-default"
                        v-on:click.prevent="remove_answer(answer)">
		  <span class="glyphicon glyphicon-remove"
                        aria-hidden="true"></span>
		</button>
	      </div>
              
	      <button type="submit" class="btn btn-default"
                      v-on:click.prevent="add_answer">
		Antwort hinzufügen
	      </button>
	    </div>
	    <hr />
	    <div>
	      <button type="submit" class="btn btn-default">
		Frage Speichern
	      </button>
	    </div>
	  </form>
	</div>
	<div class="modal-footer">
	  <button type="button" class="btn btn-default"
                  data-dismiss="modal">Schließen</button>
	</div>
      </div>
      <!-- /.modal-content -->
    </div>
    <!-- /.modal-dialog -->
  </div>
  <!-- /.modal -->
</div>
</template>

<script>
import Vue from 'vue'

Vue.directive('focus', {
    inserted: function (el) {
        el.focus();
    }
})

let QUESTION = {
  question: "",
  type: "",
  answers: []
};

function check_answer(answer) {
  if (answer.replace(/^\s+|\s+$/g, "")) {
    return answer.includes("::");
  }
  return false;
}

export default {
    methods: {
	showModal() {
	    this.modalShown = !this.modalShown;
	},
	delete_question(q) {
	    this.questions = this.questions.filter(question => question != q);
            this.save_all();
	},
	save_all() {
	    var ss = "";
	    this.questions.forEach(element => {
		let choices = [];
		element.answers.forEach(function(answer) {
		    let value = answer.value.trim();
		    if (value.length > 0) {
			choices.push(value);
		    }
		});
		ss += (element.question.trim() +
		       " => " +
		       element.type.trim() +
		       "::" +
		       choices.join("::") + '\n');
	    });
            console.log(ss);
	    this.vv = ss
	},
	remove_answer(answer) {
	    this.question.answers = (
		this.question.answers.filter(a => a != answer));
	},
	save_question() {
	    var error = false;
	    if (!this.question.question.trim()) {
		error = true;
		alert("Please fill the question.");
	    }
	    if (!this.question.type.trim()) {
		error = true;
		alert("Please select a type of question.");
	    } else {
		let choices = [];
		this.question.answers.forEach(function(answer) {
		    let value = answer.value.trim();
		    if (value.length) {
			choices.push(value);
		    }
		});
		if (choices.length < 2) {
		    alert("Please add at least 2 non-empty choices.");
		    error = true;
		}
	    }
	    if (!error) {
		this.questions.push(Object.assign({}, this.question));
		this.question.question = "";
		this.question.type = "";
		this.question.answers = [];
		this.save_all();
	    }
	},
	add_answer() {
	    this.question.answers.push(Object({ value: "" }));
	}
    },
    props: {
	questions: {
	    type: String,
	    default: ""
	}
    },
    created() {
        console.log(this.questions)
    
        if (this.questions) {
	    this.vv = this.questions;
	    this.questions = JSON.parse(this.questions);
	} else {
	    this.vv = "";
            this.questions = [];
        }
    },
    data() {
	return {
	    vv: "",
	    modalShown: false,
	    question: QUESTION,
	};
    }
};
</script>
    
<style scoped>
</style>
