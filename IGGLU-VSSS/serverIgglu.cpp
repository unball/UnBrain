#include "serverIgglu.h"
#include <QtWebSockets/QWebSocketServer>
#include <QtWebSockets/QtWebSockets>
#include <QtCore>
#include <cstdio>
#include <QDataStream>
#include <QByteArray>
#include <msgpack.hpp>
#include <map>
#include <string>

using namespace std;

QT_USE_NAMESPACE

ServerIgglu::ServerIgglu(QObject *parent)
    : QObject{parent}
{}

ServerIgglu::~ServerIgglu() {}

void ServerIgglu::connectWebSocket(quint16 port) {
    QUrl url{"ws://localhost:5001"};

    if(m_webSocket.state() == QAbstractSocket::ConnectedState){
        return;
    }

    m_webSocket.open(url);

    QTextStream(stdout) << "Connected to "<< url.toString()  <<"\n";


    connect(&m_webSocket, &QWebSocket::connected, this, &ServerIgglu::onConnected);
    connect(&m_webSocket, &QWebSocket::disconnected, this, &ServerIgglu::closeWebSocket);
}

void ServerIgglu::closeWebSocket() {
    m_webSocket.close();
    m_webSocket.disconnect();
    qDebug() << "CLOSED EWE SOCKET";
}

void ServerIgglu::onConnected() {
    connect(&m_webSocket, &QWebSocket::binaryMessageReceived,
            this, &ServerIgglu::processMessage);
}

void ServerIgglu::closed() {
// TODO is this needed?
    qDebug() << "closed";
}

void ServerIgglu::processMessage(const QByteArray &message)
{
    // Recebendo a mensagem binária empacotada do MessagePack
    std::string msg_data(message.constData(), message.size());

    try {
        // Desempacotando a mensagem
        msgpack::object_handle oh = msgpack::unpack(msg_data.data(), msg_data.size());
        msgpack::object obj = oh.get();

        // Converta o objeto para um dicionário (std::map em C++)
        std::map<std::string, msgpack::object> received_dict;
        obj.convert(received_dict);

        // Iterando sobre os elementos do dicionário e imprimindo com qDebug()
        for (const auto& pair : received_dict) {
            QTextStream(stdout) << "Key: " << QString::fromStdString(pair.first) << "- Value: ";
            
            // Verifica o tipo do valor
            if (pair.second.type == msgpack::type::ARRAY) {
                // Se o valor é um array, iteramos sobre os elementos
                std::vector<msgpack::object> array_values;
                pair.second.convert(array_values);
                for (const auto& element : array_values) {
                    if (element.type == msgpack::type::FLOAT) {
                        float float_value;
                        element.convert(float_value);
                        QTextStream(stdout) << float_value << ' ';  // Imprime valor float
                    } else {
                        QTextStream(stdout) << "Unsupported array element type";  // Caso de tipo não suportado no array
                    }
                }
                QTextStream(stdout) << "\n";
            } else if (pair.second.type == msgpack::type::MAP) {
                // Se o valor é um dicionário, convertemos para um map
                std::map<std::string, msgpack::object> inner_dict;
                pair.second.convert(inner_dict);
                for (const auto& inner_pair : inner_dict) {
                    QTextStream(stdout) << "Inner Key: " << QString::fromStdString(inner_pair.first) << "- Inner Value: ";
                    
                    // Verifica o tipo do valor no dicionário interno
                    if (inner_pair.second.type == msgpack::type::ARRAY) {
                        std::vector<msgpack::object> inner_array_values;
                        inner_pair.second.convert(inner_array_values);
                        for (const auto& element : inner_array_values) {
                            if (element.type == msgpack::type::FLOAT) {
                                float float_value;
                                element.convert(float_value);
                                QTextStream(stdout) << float_value;  // Imprime valor float
                            } else {
                                QTextStream(stdout) << "Unsupported inner array element type";  // Caso de tipo não suportado
                            }
                        }
                    } else {
                        QTextStream(stdout) << "Unsupported type in inner dictionary";  // Caso de tipo não suportado no dicionário
                    }
                }
                QTextStream(stdout) << "\n";
            } else {
                QTextStream(stdout) << "Unsupported type";  // Caso de tipo não suportado
            }
        }
    } catch (const std::exception& e) {
        qDebug() << "Error unpacking message:" << e.what();
    }
}

void ServerIgglu::sendMessage() {
    m_webSocket.sendTextMessage("message");
}
